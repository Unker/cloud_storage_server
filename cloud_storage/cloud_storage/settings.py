"""
Django settings for cloud_storage project.

Generated by 'django-admin startproject' using Django 5.0.6.

"""

from pathlib import Path
import environ
import os

env = environ.Env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY_DJANGO')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG', default='False') == 'True'

CORS_ALLOWED_HOSTS = env('CORS_ALLOWED_HOSTS', default='').split(',')
ALLOWED_HOSTS = env('ALLOWED_HOSTS', default='').split(',')

print(f'ALLOWED_HOSTS = {ALLOWED_HOSTS}')

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',

    'storage',
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    'corsheaders.middleware.CorsMiddleware',
]

valid_csrf_trusted_origins = [host for host in CORS_ALLOWED_HOSTS if host.startswith(('http://', 'https://'))]

CSRF_TRUSTED_ORIGINS = [
    'http://localhost:3000'
] + valid_csrf_trusted_origins

CORS_ORIGIN_ALLOW_ALL = True if '*' in CORS_ALLOWED_HOSTS else False

CORS_ALLOWED_ORIGINS = CORS_ALLOWED_HOSTS if not CORS_ORIGIN_ALLOW_ALL else []

print(f'CORS_ALLOWED_ORIGINS = {CORS_ALLOWED_ORIGINS}')
print(f'CSRF_TRUSTED_ORIGINS = {CSRF_TRUSTED_ORIGINS}')

# Allow credentials to be included in the requests
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_HEADERS = [
    'content-type',
    'authorization',
    'x-csrftoken',
]

ROOT_URLCONF = "cloud_storage.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

LOGIN_REDIRECT_URL = "/"

WSGI_APPLICATION = "cloud_storage.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME'),
        'HOST': env('DB_HOST', default='127.0.0.1'),
        'PORT': env('DB_PORT'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "storage.validators.CustomPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "/static/"

# статика для nginx
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

STORAGE_PATH = env('STORAGE_PATH')

# Основной URL для медиафайлов
MEDIA_URL = f"/{env('STORAGE_PATH')}/"

# Корневая директория для медиафайлов
MEDIA_ROOT = os.path.join(BASE_DIR, env('STORAGE_PATH'))

APPEND_SLASH=False

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.UserRateThrottle',
        'rest_framework.throttling.AnonRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'user': '600/minute',
        'anon': '200/minute',
    },
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 2,#20,
}

AUTH_USER_MODEL = 'storage.UserStorage'

# DJANGO_LOG_LEVEL=DEBUG

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'debug.log'),
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['console', 'file'],
            'level': 'ERROR',
            'propagate': False,
        },
        'storage': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
