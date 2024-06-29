FROM python:3.11.4-slim-buster

# Устанавливаем зависимости
RUN apt-get update \
    && apt-get install -y gcc libpq-dev

# Устанавливаем рабочую директорию
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Копируем файлы проекта
COPY . /usr/src/app

# Устанавливаем Python-зависимости
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Collect static files
RUN python manage.py collectstatic --noinput

# Запускаем приложение
CMD ["entrypoint.sh"]
