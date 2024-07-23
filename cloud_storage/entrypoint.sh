#!/bin/sh
echo "################################## Run nginx"

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $DB_HOST $DB_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

exec gunicorn --timeout 120 cloud_storage.wsgi:application --bind 0.0.0.0:8000
