import pytest
from django.urls import reverse
from rest_framework import status
from model_bakery import baker
from storage.models import UserStorage, StorageFiles

@pytest.fixture
def storage_files(users):
    files = []
    for user in users:
        user_files = baker.make(StorageFiles, owner=user, _quantity=2)
        files.extend(user_files)
    return files


@pytest.mark.django_db
def test_get_queryset(client, users, storage_files):
    '''проверяет, что аутентифицированный пользователь получает только свои файлы'''
    user = users[0]
    client.login(user)
    response = client.get(reverse('storagefiles-list'))
    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 2
    assert len(response.data['results']) == 2

@pytest.mark.django_db
def test_get_queryset_superuser(client, users, admin_user, storage_files):
    '''
    Проверяет, что суперпользователь может получить файлы
    другого пользователя, указав user_id.
    '''
    client.login(admin_user)
    response = client.get(reverse('storagefiles-list'), {'user_id': users[0].id})
    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 2

@pytest.mark.django_db
def test_by_user(client, users, storage_files):
    '''проверяет работу эндпоинта by_user с параметром user_id'''
    user = users[0]
    client = client.login(user)
    response = client.get(reverse('storagefiles-by-user'), {'user_id': user.id})
    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 2

    response = client.get(reverse('storagefiles-by-user'))
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['detail'] == 'user_id parameter is required'

@pytest.mark.django_db
def test_generate_short_link(client, users, storage_files):
    '''Проверка генерации короткой ссылки для файла'''
    user = users[0]
    file = storage_files[0]
    client = client.login(user)
    url = reverse('storagefiles-generate-short-link', kwargs={'pk': file.id})
    response = client.post(url)
    assert response.status_code == status.HTTP_200_OK
    assert 'short_link' in response.data
    file.refresh_from_db()
    assert response.data['short_link'] == file.short_link
