FROM python:3.11.4-slim-buster

# Устанавливаем зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    netcat \
    && apt-get clean

ENV APP_HOME=/usr/src/app

# Устанавливаем рабочую директорию
WORKDIR $APP_HOME

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Копируем файлы проекта
COPY . $APP_HOME

# Устанавливаем Python-зависимости
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Collect static files
RUN python manage.py collectstatic --noinput

COPY ./entrypoint.sh .
# Совместимость с windows файлами
RUN sed -i 's/\r$//g' $APP_HOME/entrypoint.sh
RUN chmod +x $APP_HOME/entrypoint.sh

# Запускаем приложение
ENTRYPOINT ["./entrypoint.sh"]
