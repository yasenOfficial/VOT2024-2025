# Terraform конфигурация за стартиране на FitnessApp контейнер

Това README описва как да използвате Terraform конфигурацията за автоматично изтегляне и стартиране на Docker контейнер, съдържащ приложението FitnessApp (Проекта по разработка).

## Описание на конфигурацията

- **Цел:** Създаване и стартиране на Docker контейнер с име `fitnessapp`, използвайки Terraform и Docker провайдър.
- **Какво прави:**  
  1. Изтегля Docker образ (`ghcr.io/yasenofficial/fitnessapp-razrabotka:sha-c0ce743`) от GitHub Container Registry.  
  2. Създава контейнер с име `fitnessapp`.  
  3. Настройва необходимите променливи на средата (environment variables) за правилното функциониране на Flask приложението.  
  4. Препраща порт 5000 (вътрешен порт на контейнера → порт 5000 на хоста).  
  5. Задава рестарт политика `unless-stopped`, така че контейнерът да се рестартира автоматично при спиране (освен ако не бъде ръчно спрян).


## Структура на файловете
```
repo/
├── main.tf
└── README.md
```


- **main.tf**  
  Съдържа Terraform код с дефиниции за `docker_image` и `docker_container`.

---

## Съдържание на `main.tf`

```hcl
terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0.2"
    }
  }
}

provider "docker" {}

resource "docker_image" "fitnessapp" {
  name         = "ghcr.io/yasenofficial/fitnessapp-razrabotka:sha-c0ce743"
  keep_locally = true
}

resource "docker_container" "fitnessapp" {
  name  = "fitnessapp"
  image = docker_image.fitnessapp.image_id

  ports {
    internal = 5000
    external = 5000
  }

  env = [
    "SECRET_KEY=your_secret_key_here",
    "DATABASE_URI=sqlite:///gamefit.db",
    "JWT_SECRET_KEY=your_jwt_secret_key_here",
    "JWT_EXPIRES_MINUTES=15",

    # Email (Flask-Mail) конфигурация
    "MAIL_SERVER=smtp.gmail.com",
    "MAIL_PORT=587",
    "MAIL_USE_TLS=True",
    "MAIL_USERNAME=???",
    "MAIL_PASSWORD=???",
    "MAIL_DEFAULT_NAME=GameFit",
    "MAIL_DEFAULT_EMAIL=???",

    # Настройки за потвърждение на имейл
    "CONFIRM_EXPIRATION=3600",

    # Flask специфични променливи
    "FLASK_APP=app.py",
    "FLASK_DEBUG=1"
  ]

  restart = "unless-stopped"
}

```

`terraform { … }`
Дефинира необходимия провайдър kreuzwerker/docker версия ~> 3.0.2.

`provider "docker" {}`
Настройва Docker провайдъра, който използва локалната Docker демо.

`resource "docker_image" "fitnessapp" { … }`
Изтегля Docker образа `ghcr.io/yasenofficial/fitnessapp-razrabotka:sha-c0ce743`.

`keep_locally = true` гарантира, че образът няма да се изтрива автоматично при docker_image унищожаване.

`resource "docker_container" "fitnessapp" { … }`
Създава контейнер: с име fitnessapp базиран на изтегления образ:
`(image = docker_image.fitnessapp.image_id)`

пренасочва порт `5000 (container → host)`

задава всички необходими променливи на средата `(env = [ … ])`

рестарт политика unless-stopped (рестартира контейнера автоматично след изключване, освен ако не е спряно ръчно).


## Стъпки за стартиране

#### Инициализация

`terraform init`
Ако всичко е наред ще видим:

```
Initializing the backend...

Initializing provider plugins...
- Finding kreuzwerker/docker versions matching "~> 3.0.2"…
- Installing kreuzwerker/docker v3.x.x…
- Installed kreuzwerker/docker v3.x.x (signed by HashiCorp)

Terraform has been successfully initialized!
```

#### Проверка на конфигурацията

`terraform validate`

При валидна конфигурация Terraform ще напише:

```
Success! The configuration is valid.
```

#### Създаване на инфраструктурата (приложение на промените)


`terraform apply`

Terraform ще покаже списък с действията, които ще извърши.

Получаваме следния prompt:

```
Do you want to perform these actions?
  Terraform will perform the actions described above.
  Only 'yes' will be accepted to approve.

Enter a value:
```
Пишем `yes`

След приключване виждаме:

```
Apply complete! Resources: 2 added, 0 changed, 0 destroyed.
```

#### Проверяваме дали контейнера е стартиран:

`docker ps`

```
CONTAINER ID   IMAGE          COMMAND           CREATED         STATUS        PORTS                    NAMES
3f16e6de6938   b23551b55beb   "python app.py"   2 seconds ago   Up 1 second   0.0.0.0:5000->5000/tcp   fitnessapp
```

#### Тестваме приложението като отворим

`http://localhost:5000/`


#### За унищожаване на контейнера и образа:

`terraform destroy`