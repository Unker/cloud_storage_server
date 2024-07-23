Cloud storage server
===============

Серверная часть приложения "облачное хранилище". Приложение позволяет пользователям загружать, отправлять, скачивать файлы.

***Содержание:***

- [Технологии](#технологии)
- [Начало работы](#начало-работы)
  - [Настройка сервера](#настройка-сервера)
    - [Настройка БД](#настройка-бд)
    - [Клонирование проекта](#клонирование-проекта)
    - [Настройка переменных окружения](#настройка-переменных-окружения)
  - [Ручной запуск проекта](#ручной-запуск-проекта)
  - [Запуск проекта через Docker Compose (рекомендуется)](#run-docker)
- [Тестирование](#тестирование)
- [To do](#to-do)


# Технологии <a name="технологии"></a>

Сервер реализован на языке [Python](https://www.python.org/) с использованием фреймворка 
[Django](https://www.djangoproject.com/) и СУБД [PostgreSQL](https://www.postgresql.org/)


# Начало работы <a name="начало-работы"></a>

### Настройка сервера <a name="настройка-сервера"></a>

#### <ins>Настройка БД:</ins> <a name="настройка-бд"></a>
1. Установите PostgreSQL:
    ```bash
    sudo apt install postgresql
    ```
   
1. Создайте суперпользователя БД:
    ```bash
    sudo su postgres
    psql
    CREATE USER <имя_пользователя> WITH SUPERUSER;
    ALTER USER <имя_пользователя> WITH PASSWORD <пароль>;
    CREATE DATABASE <имя_пользователя>;
    \q
    exit
    ```

1. Зайдите в управление БД от суперпользователя и создайте БД для приложения:
    ```bash
    psql
    CREATE DATABASE cloud_storage_db;
    exit
    ```
#### <ins>Клонирование проекта:</ins> <a name="клонирование-проекта"></a>
```bash
git clone https://github.com/Unker/cloud_storage_server.git
cd cloud_storage_server/cloud_storage/
```
   
#### <ins>Настройка переменных окружения:</ins> <a name="настройка-переменных-окружения"></a>
1. Создайте .env файл и откройте на редактирование:
   ```bash
   touch .env
   nano .env
   ```
   
1. Сгенерируйте SECRET_KEY в Django:
   ```bash
   python3 manage.py shell
   from django.core.management import utils
   utils.get_random_secret_key()
   exit()
   ```
   
1. Заполните .env следующим содержимым:
   ```
   SECRET_KEY_DJANGO='django-insecure-xxx'
   CORS_ALLOWED_HOSTS='http://localhost:3000,http://109.71.245.96:3000'
   ALLOWED_HOSTS='localhost,0.0.0.0,109.71.245.96'
   DB_NAME=cloud_storage_db
   DB_HOST=109.71.245.96
   DB_PORT=5432
   DB_USER=<имя_суперпользователя>
   DB_PASSWORD=<пароль_суперпользователя>
   STORAGE_PATH=users_files
   ```
    - Вместо `xxx` в `SECRET_KEY_DJANGO` вставьте ключ, полученный в предыдущем действии.
    - Для полей `CORS_ALLOWED_HOSTS` и `ALLOWED_HOSTS` вместо `109.71.245.96` укажите адреса вашего frontend
    - Для поля `DB_HOST` - текущий адрес сервера
    - Для `DB_USER` - имя вашего суперпользователя
    - Для `DB_PASSWORD` - пароль вашего суперпользователя

1. Редактирование настройки nginx. Замените значение в параметре `server_name` на ip адрес вашего сервера
    ```bash
    nano nginx/server.backend.conf
    ```

   

## Ручной запуск проекта <a name="начало-работы"></a>

#### <ins>Настройка Django:</ins>
1. Создайте виртуальное окружение и запустите его. В каталоге с проектом выполните команды:
    ```bash
    cd cloud_storage/   (если еще не в каталоге с проектом)
    python3 -m venv venv
    ```
    ```bash
    source venv/bin/activate
    ```

1. Установите зависимости:
    ```bash
    pip install -r requirements.txt
    ```

1. Сделайте миграции 
    ```bash
    python manage.py migrate
    ```

1. Создайте суперпользователя для управления Django приложением
    ```bash
    python manage.py createsuperuser
    ```

1. Сборка статики на сервере:
    ```bash
    python manage.py collectstatic
    ```

#### <ins>Запуск приложения:</ins>
1. Запустите сервер:
    ```bash
    python manage.py runserver 0.0.0.0:8000
    ```
***Внимание! Запуск сервера выполнять внутри окружения Python, созданного выше***

## Запуск проекта через Docker Compose <a name="run-docker"></a>
1. [Установите Docker](https://docs.docker.com/engine/install/ubuntu/)
1. Запустите систему сборки контейнеров:
    ```bash
    docker compose -f docker-compose.prod.yml up -d --build
    ```

1. Проверьте, что контейнер запущен:
    ```bash
    docker ps
    ```

1. Должны быть активны образы: `nginx:stable-alpine` и `cloud_storage_server-backend`


## Тестирование <a name="тестирование"></a>

Проект покрыт юнит-тестами. Для их запуска выполните действия ниже
1. Установите дополнительные зависимости:
    ```bash
    pip install -r requirements-dev.txt
    ```

1. Для их запуска выполните команду:
    ```bash
    pytest
    ```

## Todo <a name="to-do"></a>

Настроить CI\CD