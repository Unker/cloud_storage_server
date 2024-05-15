from bs4 import BeautifulSoup

import pytest
from django.contrib.auth.hashers import make_password
from rest_framework.authtoken.models import Token
from rest_framework.reverse import reverse
from model_bakery import baker
from rest_framework.test import APIClient
from rest_framework import status
from django.test.client import encode_multipart

from storage.models import UserStorage


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def users_factory():
    def factory(count_users=5, *args, **kwargs):
        users_set = baker.prepare(UserStorage, _quantity=count_users)

        # Хешируем пароли для каждого пользователя
        for idx, user in enumerate(users_set, start=0):
            # Создаем пароли для пользователей в виде строк "password1", "password2" и т.д.
            user.password = make_password(f'password{idx}')
            user.save()
        return users_set

    return factory


@pytest.fixture
def users(users_factory):
    n_users = 10
    return users_factory(_quantity=n_users)


def get_error_list(html):
    ''' Находим все теги <ul> с классом "errorlist" '''
    soup = BeautifulSoup(html, 'html.parser')
    return soup.find_all('ul', class_='errorlist')


def post_form_data(client, url, data):
    ''' Отправка формы '''
    content = encode_multipart('BoUnDaRyStRiNg', data)
    content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
    return client.post(url, content, content_type=content_type)


@pytest.mark.django_db
def test_login_user(client, users):
    """ проверка login пользователя """
    url = '/accounts/login/'
    username = users[0].username
    password = 'password0'

    #
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK

    data = {
        'username': username,
        'password': 'badpass',
    }
    response = post_form_data(client, url, data)
    assert response.status_code == status.HTTP_200_OK

    error_lists = get_error_list(response.content)
    assert len(error_lists) == 1

    data = {
        'username': username,
        'password': password,
    }
    response = post_form_data(client, url, data)
    assert response.status_code == status.HTTP_302_FOUND


@pytest.mark.django_db
def test_logout_user(client, users):
    """ проверка logout пользователя """
    url = '/accounts/logout/'
    username = users[0].username
    data = {
        'username': username,
    }

    response = post_form_data(client, url, data)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_custom_register(client):
    """ проверка регистрации пользователя """
    url = reverse('custom_register')

    data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'first_name': 'FirstName',
        'last_name': 'LastName',
        'password1': 'testpassword',
        'password2': 'testpassword',
    }

    response = post_form_data(client, url, data)
    assert response.status_code == status.HTTP_200_OK

    error_lists = get_error_list(response.content)
    assert len(error_lists) == 0

    # Проверяем, что пользователь создался
    assert UserStorage.objects.filter(username=data['username']).exists()


    # Пытаемся создать пользователя с тем же username
    data2 = data.copy()
    data2["email"] = 'test2@example.com'
    response = post_form_data(client, url, data2)
    assert response.status_code == status.HTTP_200_OK
    error_lists = get_error_list(response.content)
    assert len(error_lists) == 1
    # Проверяем, что пользователь не создался
    assert not UserStorage.objects.filter(email=data2['email']).exists()


    # Пытаемся создать пользователя с тем же email
    data3 = data.copy()
    data3["username"] = 'testuser2'
    response = post_form_data(client, url, data3)
    assert response.status_code == status.HTTP_200_OK
    error_lists = get_error_list(response.content)
    assert len(error_lists) == 1


    # не совпадают пароли
    data4 = {
        'username': 'testuser4',
        'email': 'test4@example.com',
        'first_name': 'FirstName',
        'last_name': 'LastName',
        'password1': 'testpassword',
        'password2': 'wrongpassword',
    }

    response = post_form_data(client, url, data4)
    assert response.status_code == status.HTTP_200_OK
    error_lists = get_error_list(response.content)
    assert len(error_lists) == 1


@pytest.mark.django_db
def test_get_users(client, users):
    """ проверка получения списка пользователей """
    url = '/users/?page=1'
    # header = {
    #     'Authorization': 'Token 7fcf74524c7bc3509f0bede2e93dca1723172718',
    # }

    # token = Token.objects.get(user__username=users[0].username)
    admin = UserStorage.objects.create_superuser('admin', 'admin@admin.com', 'admin123')
    token = Token.objects.create(user=admin)

    response = client.get(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    response = client.get(url, HTTP_AUTHORIZATION='Token ' + token.key)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == UserStorage.objects.all().count()
