import os

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from model_bakery import baker
from storage.models import UserStorage, StorageFiles

@pytest.fixture
def storage_files(users):
    '''генератор файлов для пользователей'''
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
def test_by_user(client, users, admin_user, storage_files):
    '''проверяет работу эндпоинта by_user с параметром user_id'''
    user = users[0]
    client =  client.login(admin_user)
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


@pytest.mark.django_db
def test_create_file(client, users, storage_files):
    '''Проверка создания нового файла'''
    user = users[0]
    client = client.login(user)
    url = reverse('storagefiles-list')

    file = SimpleUploadedFile("testfile.txt", b"file_content", content_type="text/plain")

    data = {
        'comment': 'testcomment',
        'file': file,
    }

    count_files = StorageFiles.objects.count()

    response = client.post(url, data, format='multipart')
    assert response.status_code == status.HTTP_201_CREATED

    new_count_files = StorageFiles.objects.count()
    assert new_count_files == count_files + 1

    # проверяем ответ от сервера
    assert response.data['original_name'] == file.name
    assert response.data['owner'] == user.id
    assert response.data['file'] != None
    assert response.data['size'] == file.size
    assert response.data['upload_date'] != None
    assert response.data['last_update_date'] != None
    assert response.data['comment'] == data['comment']

    # проверяем содержимое БД
    new_file = StorageFiles.objects.latest('id')
    assert new_file.original_name == file.name
    assert new_file.owner.id == user.id
    assert new_file.file != None
    assert new_file.size == file.size
    assert new_file.upload_date != None
    assert new_file.last_update_date != None
    assert new_file.comment == data['comment']

    # Проверка, что файл действительно создан
    file_path = new_file.file.path
    assert os.path.exists(file_path)

@pytest.mark.django_db
def test_update_file(client, users, storage_files):
    '''Проверка обновления информации о файле'''
    user = users[0]
    file = storage_files[0]
    client = client.login(user)
    url = reverse('storagefiles-detail', kwargs={'pk': file.id})

    new_file = SimpleUploadedFile("testfile.txt", b"file_content", content_type="text/plain")

    data = {
        'comment': 'testcomment',
        'file': new_file,
    }

    response = client.put(url, data, format='multipart')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['comment'] == data['comment']
    file.refresh_from_db()
    assert file.comment == data['comment']


@pytest.mark.django_db
def test_partial_update_file(client, users, storage_files):
    '''Проверка частичного обновления информации о файле'''
    user = users[0]
    file = storage_files[0]
    client = client.login(user)
    url = reverse('storagefiles-detail', kwargs={'pk': file.id})

    data = {
        'comment': 'newcomment'
    }

    response = client.patch(url, data)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['comment'] == data['comment']
    file.refresh_from_db()
    assert file.comment == data['comment']


@pytest.mark.django_db
def test_delete_file(client, users, storage_files):
    '''Проверка удаления файла'''
    user = users[0]
    # file = users_files[0]
    client = client.login(user)
    url = reverse('storagefiles-list')

    file = SimpleUploadedFile("testfile.txt", b"file_content", content_type="text/plain")

    data = {
        'comment': 'testcomment',
        'file': file,
    }

    response = client.post(url, data, format='multipart')
    assert response.status_code == status.HTTP_201_CREATED
    new_file = StorageFiles.objects.latest('id')

    url = reverse('storagefiles-detail', kwargs={'pk': new_file.id})

    response = client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not StorageFiles.objects.filter(pk=new_file.id).exists()
