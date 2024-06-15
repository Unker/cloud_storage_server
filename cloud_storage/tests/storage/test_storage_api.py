import os

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from model_bakery import baker
from storage.models import UserStorage, StorageFiles


@pytest.fixture
def storage_files(users):
    """Генератор файлов для пользователей"""
    files = []
    for user in users:
        user_files = baker.make(StorageFiles, owner=user, _quantity=2)
        files.extend(user_files)
    return files


@pytest.mark.django_db
def test_get_queryset(client, users, storage_files):
    """Проверяет, что аутентифицированный пользователь получает только свои файлы"""
    user = users[0]
    client.login(user)
    response = client.get(reverse('storagefiles-list'))
    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 2
    assert len(response.data['results']) == 2


@pytest.mark.django_db
def test_access_file_without_permission(client, users, storage_files):
    """Проверка доступа к файлу без разрешения"""
    user = users[1]  # Different user
    file = storage_files[0]
    client.login(user)
    url = reverse('storagefiles-detail', kwargs={'pk': file.id})

    response = client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "No StorageFiles matches the given query." in response.data['detail']


@pytest.mark.django_db
def test_get_queryset_superuser(client, users, admin_user, storage_files):
    """
    Проверяет, что суперпользователь может получить файлы
    другого пользователя, указав user_id.
    """
    client.login(admin_user)
    response = client.get(reverse('storagefiles-list'))
    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == len(storage_files)


@pytest.mark.django_db
def test_by_user(client, users, admin_user, storage_files):
    """проверяет работу эндпоинта by_user с параметром user_id"""
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
    """Проверка генерации короткой ссылки для файла"""
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
def test_create_file(client, users, storage_files, cleanup):
    """Проверка создания нового файла"""
    user = users[0]
    client = client.login(user)
    url = reverse('storagefiles-list')

    file = SimpleUploadedFile("testfile.txt", b"file_content", content_type="text/plain")

    data = {
        'comment': 'test-comment',
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
    assert response.data['file'] is not None
    assert response.data['size'] == file.size
    assert response.data['upload_date'] is not None
    assert response.data['last_update_date'] is not None
    assert response.data['comment'] == data['comment']

    # проверяем содержимое БД
    new_file = StorageFiles.objects.latest('id')
    assert new_file.original_name == file.name
    assert new_file.owner.id == user.id
    assert new_file.file is not None
    assert new_file.size == file.size
    assert new_file.upload_date is not None
    assert new_file.last_update_date is not None
    assert new_file.comment == data['comment']

    # Проверка, что файл действительно создан
    file_path = new_file.file.path
    assert os.path.exists(file_path)
    cleanup(user.username)


@pytest.mark.django_db
def test_create_file_with_invalid_data(client, users):
    """Проверка создания файла с недопустимыми данными"""
    user = users[0]
    client.login(user)
    url = reverse('storagefiles-list')

    # Omit the file field entirely to simulate invalid data
    data = {
        'comment': 'test-comment'
    }

    response = client.post(url, data, format='multipart')
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    # Pass an invalid file-like object
    invalid_file = SimpleUploadedFile("invalid.txt", b"", content_type="text/plain")
    data = {
        'comment': 'test-comment',
        'file': invalid_file
    }

    response = client.post(url, data, format='multipart')
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_update_file(client, users, admin_user, storage_files, cleanup):
    """Проверка обновления информации о файле"""
    user = users[0]
    other_user = users[1]
    file = storage_files[0]
    client_user = client.login(user)
    url = reverse('storagefiles-detail', kwargs={'pk': file.id})

    new_file = SimpleUploadedFile("testfile.txt", b"file_content", content_type="text/plain")

    data = {
        'comment': 'test-comment',
        'file': new_file,
    }

    # Проверка обновления файла самим пользователем
    response = client_user.put(url, data, format='multipart')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['comment'] == data['comment']
    file.refresh_from_db()
    assert file.comment == data['comment']

    # Обновление данных для следующего запроса
    data['file'] = SimpleUploadedFile("testfile.txt", b"file_content", content_type="text/plain")
    admin_comment = 'admin-test-comment'
    data['comment'] = admin_comment

    # Проверка обновления файла администратором
    client_admin = client.login(admin_user)
    response = client_admin.put(url, data, format='multipart')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['comment'] == data['comment']
    file.refresh_from_db()
    assert file.comment == data['comment']

    # Обновление данных для следующего запроса
    data['file'] = SimpleUploadedFile("testfile.txt", b"file_content", content_type="text/plain")
    data['comment'] = 'other_user-test-comment'

    # Проверка запрета обновления файла другим пользователем
    client_other_user = client.login(other_user)
    response = client_other_user.put(url, data, format='multipart')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    file.refresh_from_db()
    assert file.comment == admin_comment

    cleanup(user.username)


@pytest.mark.django_db
def test_partial_update_file(client, users, storage_files, cleanup):
    """Проверка частичного обновления информации о файле"""
    user = users[0]
    file = storage_files[0]
    client = client.login(user)
    url = reverse('storagefiles-detail', kwargs={'pk': file.id})

    data = {
        'comment': 'new comment'
    }

    response = client.patch(url, data)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['comment'] == data['comment']
    file.refresh_from_db()
    assert file.comment == data['comment']
    cleanup(user.username)


@pytest.mark.django_db
def test_delete_file(client, users, storage_files):
    """Проверка удаления файла"""
    user = users[0]
    client = client.login(user)
    url = reverse('storagefiles-list')

    file = SimpleUploadedFile("testfile.txt", b"file_content", content_type="text/plain")

    data = {
        'comment': 'test-comment',
        'file': file,
    }

    response = client.post(url, data, format='multipart')
    assert response.status_code == status.HTTP_201_CREATED
    new_file = StorageFiles.objects.latest('id')

    url = reverse('storagefiles-detail', kwargs={'pk': new_file.id})

    response = client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not StorageFiles.objects.filter(pk=new_file.id).exists()
