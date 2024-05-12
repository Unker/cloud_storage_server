from urllib.parse import urlencode
from bs4 import BeautifulSoup

import pytest
from django.contrib.auth.hashers import make_password
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


@pytest.mark.django_db
def test_login_user(client, users):
    """ проверка login пользователя """
    username = users[0].username
    password = 'password0'

    response = client.get(reverse('custom_login'))
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    response = client.post(reverse('custom_login'),
                            {
                                'username': username,
                                'password': 'badpass',
                            },
                        )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    response = client.post(reverse('custom_login'),
                            {
                                'username': username,
                                'password': password,
                            },
                        )
    assert response.status_code == status.HTTP_200_OK


def get_error_list(html):
    ''' Находим все теги <ul> с классом "errorlist" '''
    soup = BeautifulSoup(html, 'html.parser')
    return soup.find_all('ul', class_='errorlist')

def post_form_data(client, data):
    content = encode_multipart('BoUnDaRyStRiNg', data)
    content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
    return client.post(reverse('custom_register'), content, content_type=content_type)



@pytest.mark.django_db
def test_custom_register(client):
    """ проверка регистрации пользователя """

    data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'first_name': 'FirstName',
        'last_name': 'LastName',
        'password1': 'testpassword',
        'password2': 'testpassword',
    }

    response = post_form_data(client, data)
    assert response.status_code == status.HTTP_200_OK

    error_lists = get_error_list(response.content)
    assert len(error_lists) == 0

    # Проверяем, что пользователь создался
    assert UserStorage.objects.filter(username=data['username']).exists()


    # Пытаемся создать пользователя с тем же username
    data2 = data.copy()
    data2["email"] = 'test2@example.com'
    response = post_form_data(client, data2)
    assert response.status_code == status.HTTP_200_OK
    error_lists = get_error_list(response.content)
    assert len(error_lists) == 1
    # Проверяем, что пользователь не создался
    assert not UserStorage.objects.filter(email=data2['email']).exists()


    # Пытаемся создать пользователя с тем же email
    data3 = data.copy()
    data3["username"] = 'testuser2'
    response = post_form_data(client, data3)
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

    response = post_form_data(client, data4)
    assert response.status_code == status.HTTP_200_OK
    error_lists = get_error_list(response.content)
    assert len(error_lists) == 1
