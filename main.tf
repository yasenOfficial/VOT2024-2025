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

    # Email (Flask-Mail) configuration
    "MAIL_SERVER=smtp.gmail.com",
    "MAIL_PORT=587",
    "MAIL_USE_TLS=True",
    "MAIL_USERNAME=???w",
    "MAIL_PASSWORD=???",
    "MAIL_DEFAULT_NAME=GameFit",
    "MAIL_DEFAULT_EMAIL=???",

    # Email confirmation settings
    "CONFIRM_EXPIRATION=3600",

    # Flask environment
    "FLASK_APP=app.py",
    "FLASK_DEBUG=1"
    # (removed duplicate JWT_EXPIRES_MINUTES here)
  ]

  restart = "unless-stopped"
}
