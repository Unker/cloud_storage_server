import os

import shortuuid
from django.contrib.auth.models import User, AbstractUser
from django.db import models

from cloud_storage.settings import STORAGE_PATH


class UserStorage(AbstractUser):
    '''Пользователи'''
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    storage_path = models.CharField(max_length=255)

    def __str__(self):
        return self.username


def user_directory_path(instance, filename):
    # file will be uploaded to STORAGE_PATH/<username>/<filename>
    return os.path.join(STORAGE_PATH, instance.owner.username, filename)

class StorageFiles(models.Model):
    '''Файлы пользователя'''
    owner = models.ForeignKey(UserStorage, on_delete=models.CASCADE)
    original_name = models.CharField(max_length=255)
    file = models.FileField(
        upload_to=user_directory_path,
        max_length = 255,
    )
    size = models.BigIntegerField(editable=False)
    upload_date = models.DateTimeField(auto_now_add=True)
    last_update_date = models.DateTimeField(auto_now=True)
    last_download_date = models.DateTimeField(null=True, blank=True)
    comment = models.TextField(blank=True)
    short_link = models.CharField(max_length=255, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.owner_id and 'owner' in kwargs:
            self.owner = kwargs.pop('owner')
        if self.file:
            self.size = self.file.size
            self.original_name = self.file.name
        super(StorageFiles, self).save(*args, **kwargs)

    def __str__(self):
        return self.original_name

    def generate_short_link(self):
        self.short_link = shortuuid.uuid()
        self.save()
