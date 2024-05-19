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


class StorageFiles(models.Model):
    '''Файлы пользователя'''
    owner = models.ForeignKey(UserStorage, on_delete=models.CASCADE)
    original_name = models.CharField(max_length=255)
    file = models.FileField(upload_to=STORAGE_PATH, null=True, blank=True)
    size = models.BigIntegerField(editable=False)
    upload_date = models.DateTimeField(auto_now_add=True)
    last_update_date = models.DateTimeField(auto_now=True)
    last_download_date = models.DateTimeField(null=True, blank=True)
    comment = models.TextField(blank=True)
    short_link = models.CharField(max_length=255, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.file:
            self.size = self.file.size
        super(StorageFiles, self).save(*args, **kwargs)

    def __str__(self):
        return self.original_name

    def generate_short_link(self):
        self.short_link = shortuuid.uuid()
        self.save()
