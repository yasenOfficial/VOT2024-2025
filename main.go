package main

import (
	"database/sql"
	"log"
	"net/http"
	"os"

	"github.com/gin-gonic/gin"
	_ "github.com/lib/pq"
)

type Order struct {
	ID      int    `json:"id"`
	Product string `json:"product"`
	Address string `json:"address"`
	Phone   string `json:"phone"`
}

func initDB() (*sql.DB, error) {
	dbUser := os.Getenv("DB_USER")
	dbPassword := os.Getenv("DB_PASSWORD")
	dbName := os.Getenv("DB_NAME")

	connStr := "host=db user=" + dbUser + " password=" + dbPassword + " dbname=" + dbName + " sslmode=disable"
	db, err := sql.Open("postgres", connStr)
	if err != nil {
		return nil, err
	}

	// Create table if not exists
	createTableQuery := `
	CREATE TABLE IF NOT EXISTS orders (
		id SERIAL PRIMARY KEY,
		product TEXT NOT NULL,
		address TEXT NOT NULL,
		phone TEXT NOT NULL
	);
	`
	_, err = db.Exec(createTableQuery)
	if err != nil {
		return nil, err
	}
	return db, nil
}

func main() {
	db, err := initDB()
	if err != nil {
		log.Fatal("Could not connect to the database:", err)
	}
	defer db.Close()

	router := gin.Default()
	router.LoadHTMLGlob("templates/*")

	router.GET("/", func(c *gin.Context) {
		c.HTML(http.StatusOK, "index.html", nil)
	})

	router.POST("/order", func(c *gin.Context) {
		product := c.PostForm("product")
		address := c.PostForm("address")
		phone := c.PostForm("phone")
		if product == "" || address == "" || phone == "" {
			c.String(http.StatusBadRequest, "All fields are required")
			return
		}

		_, err := db.Exec("INSERT INTO orders (product, address, phone) VALUES ($1, $2, $3)", product, address, phone)
		if err != nil {
			c.String(http.StatusInternalServerError, "Failed to save order")
			return
		}
		c.Redirect(http.StatusFound, "/orders")
	})

	router.GET("/orders", func(c *gin.Context) {
		rows, err := db.Query("SELECT id, product, address, phone FROM orders")
		if err != nil {
			c.String(http.StatusInternalServerError, "Failed to retrieve orders")
			return
		}
		defer rows.Close()

		var orders []Order
		for rows.Next() {
			var order Order
			if err := rows.Scan(&order.ID, &order.Product, &order.Address, &order.Phone); err != nil {
				c.String(http.StatusInternalServerError, "Failed to scan order")
				return
			}
			orders = append(orders, order)
		}

		c.HTML(http.StatusOK, "orders.html", gin.H{
			"orders": orders,
		})
	})

	router.Run(":8080")
}
