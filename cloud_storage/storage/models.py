from django.contrib.auth.models import User, AbstractUser
from django.db import models


class UserStorage(AbstractUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    storage_path = models.CharField(max_length=255)

    def __str__(self):
        return self.username
