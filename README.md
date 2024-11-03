# Pizza Order Web Application

## Overview

Dockerized web app that allows users to place pizza orders.

## Technologies Used

- **Go (Golang) & Gin**
- **PostgreSQL**
- **HTML/CSS**
- **Docker**

## Project Structure

```
/project
│
├── /templates
│   ├── index.html
│   └── orders.html
├── .env
├── docker-compose.yml
├── Dockerfile
├── go.mod
├── go.sum
└── main.go
```

### Files Explained

- **Dockerfile**: Instructions to build the Docker image for the Go application.
- **docker-compose.yml**: A file used to define and run multi-container Docker applications. It specifies the services (web and db).

## Dockerfile

```
# Use an official Golang runtime (version that I have installed)
FROM golang:1.23.1

# Set the Current Working Dir inside the container
WORKDIR /app

# Copy go.mod and go.sum files
COPY go.mod ./
COPY go.sum ./

# Install requirements 
RUN go mod download

# Copy the code
COPY . .

# Build 
RUN go build -o main .

# Expose port 8080
EXPOSE 8080

# run
CMD ["./main"]

```

### Docker Compose

```
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8080:8080"
    depends_on:
      - db
    env_file:
      - .env  # Load environment variables from the .env file

  db:
    image: postgres:latest
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ${DB_NAME}
    volumes:
      - db_data:/var/lib/postgresql/data

volumes:
  db_data:
```

### Configuration Explanation:
- web: This service builds the Go application and exposes port 8080.
- db: This service runs the PostgreSQL database container and uses environment variables for configuration.
- volumes: Ensures that the database data is continued across container restarts.

## Setting Up the Application

Follow these steps to get the application up and running:

1. **Clone the Repository**: 
   Download or clone this repository to your local machine.

   ```
   git clone https://github.com/yourusername/pizza-order-app.git
   cd pizza-order-app

2. **Create env file**
    ```
    DB_USER=yourusername
    DB_PASSWORD=yourpassword
    DB_NAME=app
    ```

3. **Build & Run**s
    ```
    docker-compose up --build
    ```
