# Дипломный проект по профессии «Fullstack-разработчик на Python»

Серверная часть приложения "облачное хранилище". Приложение позволяет пользователям отображать, загружать, отправлять, 
скачивать и переименовывать файлы.

Сервер реализован на языке Python с использованием фреймворка Django и СУБД PostgreSQL.

## Инструкция по работе
#### Для запуска проекта необходимо:

1. Установить зависимости:
```bash
pip install -r requirements.txt
```

2. Сделать миграции 
```bash
python manage.py migrate
```

3. Создать суперпользователя
```bash
python manage.py createsuperuser
```

4. Сборка статики на сервере:
```bash
python manage.py collectstatic
```

5. Запустить сервер:
```bash
python manage.py runserver
```

#### Настройка БД на сервере:
1. Создадим суперпользователя БД:
```bash
sudo su postgres
psql
CREATE USER unker WITH SUPERUSER;
ALTER USER unker WITH PASSWORD '12345';
CREATE DATABASE unker;
\q
exit
```

2. Зайдем в управление БД от суперпользователя и создадим БД для приложения:
```bash
psql
CREATE DATABASE cloud_storage_db;
exit
```