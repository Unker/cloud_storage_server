Cloud Storage Server
===============

This is the server-side application for "Cloud Storage". The application allows users to upload, send, and download files.

***Contents:***

- [Technologies](#technologies)
- [Getting Started](#getting-started)
  - [Server Setup](#server-setup)
    - [Database Setup](#database-setup)
    - [Database Access](#database-access)
    - [Cloning the Project](#cloning-the-project)
    - [Setting Environment Variables](#setting-environment-variables)
  - [Manual Project Launch](#manual-project-launch)
  - [Running the Project with Docker Compose (recommended)](#run-with-docker)
- [Testing](#testing)
- [To Do](#to-do)

# Technologies <a name="technologies"></a>

The server is implemented in [Python](https://www.python.org/) using the [Django](https://www.djangoproject.com/) framework and the [PostgreSQL](https://www.postgresql.org/) database system.

# Getting Started <a name="getting-started"></a>

### Server Setup <a name="server-setup"></a>

#### <ins>Database Setup:</ins> <a name="database-setup"></a>
1. Install PostgreSQL:
    ```bash
    sudo apt install postgresql
    ```

1. Create a database superuser:
    ```bash
    sudo su postgres
    psql
    CREATE USER <username> WITH SUPERUSER;
    ALTER USER <username> WITH PASSWORD '<password>';
    CREATE DATABASE <username>;
    \q
    exit
    ```

1. Access the database management console as the superuser and create a database for the application:
    ```bash
    psql
    CREATE DATABASE cloud_storage_db;
    exit
    ```

#### <ins>Database Access:</ins> <a name="database-access"></a>
1. Configure PostgreSQL to accept connections from your local IP:
    ```bash
    sudo nano /etc/postgresql/16/main/postgresql.conf
    ```
    then set `listen_addresses` and save file
    ```
    listen_addresses = 'localhost'
    ```

1. Providing access to all IP addresses on the Docker network
    ```bash
    sudo nano /etc/postgresql/16/main/pg_hba.conf
    ```
    then add this line and save file
    ```
    host    all             all             172.18.0.0/16           md5
    ```
    This rule will allow all containers on the Docker network to connect to PostgreSQL using password access (md5 method). If you need SSL encryption, you can replace md5 with scram-sha-256.

1. Restart PostgreSQL for the changes to take effect
    ```bash
    sudo systemctl restart postgresql
    ```


#### <ins>Cloning the Project:</ins> <a name="cloning-the-project"></a>
```bash
git clone https://github.com/Unker/cloud_storage_server.git
cd cloud_storage_server/cloud_storage/
```

#### <ins>Setting Environment Variables:</ins> <a name="setting-environment-variables"></a>
1. Generate a SECRET_KEY for Django:
   ```bash
   python3 manage.py shell
   from django.core.management import utils
   utils.get_random_secret_key()
   exit()
   ```

1. Create a .env file and open it for editing:
   ```bash
   touch .env
   nano .env
   ```

1. Populate the .env file with the following content:
   ```
   SECRET_KEY_DJANGO='django-insecure-xxx'
   CORS_ALLOWED_HOSTS='http://localhost:3000,http://109.71.245.96:3000'
   ALLOWED_HOSTS='localhost,0.0.0.0,109.71.245.96'
   DB_NAME=cloud_storage_db
   DB_HOST=109.71.245.96
   DB_PORT=5432
   DB_USER=<superuser_name>
   DB_PASSWORD=<superuser_password>
   STORAGE_PATH=users_files
   ```
    - Replace `xxx` in `SECRET_KEY_DJANGO` with the key created in the previous step.
    - For `CORS_ALLOWED_HOSTS` and `ALLOWED_HOSTS`, replace `109.71.245.96` with your frontend addresses.
    - For `DB_HOST`, use the current server address.
    - For `DB_USER`, use your superuser name.
    - For `DB_PASSWORD`, use your superuser password.

1. Edit the nginx configuration. Replace the `server_name` value with the IP address of your server:
    ```bash
    nano nginx/server.backend.conf
    ```

## Manual Project Launch <a name="manual-project-launch"></a>

#### <ins>Django Setup:</ins>
1. Create and activate a virtual environment. In the project directory, run:
    ```bash
    cd cloud_storage_server/   (if not already in the project directory)
    ```
    ```bash
    python3 -m venv venv
    ```
    ```bash
    source venv/bin/activate
    ```

1. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

1. Apply migrations:
    ```bash
    python manage.py migrate
    ```

1. Create a superuser to manage the Django application:
    ```bash
    python manage.py createsuperuser
    ```

1. Collect static files on the server:
    ```bash
    python manage.py collectstatic
    ```

#### <ins>Running the Application:</ins>
1. Start the server:
    ```bash
    python manage.py runserver 0.0.0.0:8000
    ```
***Note: Ensure the server is started within the Python virtual environment created above.***

## Running the Project with Docker Compose <a name="run-with-docker"></a>

1. [Install Docker](https://docs.docker.com/engine/install/ubuntu/)
1. Start the container build system:
    ```bash
    docker compose -f docker-compose.prod.yml up -d --build
    ```

1. Check that the containers are running:
    ```bash
    docker ps
    ```

1. The `nginx:stable-alpine` and `cloud_storage_server-backend` images should be active.

## Testing <a name="testing"></a>

The project is covered by unit tests. To run the tests, follow the steps below:
1. Install additional dependencies:
    ```bash
    pip install -r requirements-dev.txt
    ```

1. Run the tests with the command:
    ```bash
    pytest
    ```

## To Do <a name="to-do"></a>

Set up CI/CD.