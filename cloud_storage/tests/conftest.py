import pytest
from django.middleware.csrf import get_token
from django.urls import reverse
from model_bakery import baker
from django.contrib.auth.hashers import make_password
from rest_framework.test import APIClient
from storage.models import UserStorage

@pytest.fixture
def client():
    # return APIClient()
    client = APIClient()

    def login(user):
        # Логин пользователя
        client.force_authenticate(user=user)
        # Получение CSRF-токена
        response = client.get(reverse('api-csrf'))
        client.cookies['csrftoken'] = response.cookies['csrftoken'].value
        return client

    client.login = login
    return client

@pytest.fixture
def users_factory():
    def factory(count_users=5, *args, **kwargs):
        users_set = baker.make(UserStorage, _quantity=count_users)

        # Хешируем пароли для каждого пользователя
        for idx, user in enumerate(users_set, start=0):
            # Создаем пароли для пользователей в виде строк "password1", "password2" и т.д.
            user.password = make_password(f'password{idx}')
            user.save()
        return users_set

    return factory

@pytest.fixture
def users(users_factory):
    n_users = 3
    return users_factory(count_users=n_users)

@pytest.fixture
def admin_user():
    return baker.make(UserStorage, is_superuser=True, password=make_password('adminpassword'))
