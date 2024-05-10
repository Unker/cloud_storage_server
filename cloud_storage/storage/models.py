from django.contrib.auth.models import User
from django.db import models

class UserStorage(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    storage_path = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'User Storage'
        verbose_name_plural = 'User Storage'

    def __str__(self):
        return self.user.username
