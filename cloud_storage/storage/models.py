from django.contrib.auth.models import User, AbstractUser
from django.db import models


# class CustomUser(AbstractUser):
#     email = models.EmailField(unique=True)
#     first_name = models.CharField(_("first name"), max_length=150)
#     last_name = models.CharField(_("last name"), max_length=150)
#     storage_path = models.CharField(max_length=255)
#
#     def __str__(self):
#         return self.username


class UserStorage(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    storage_path = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'User Storage'
        verbose_name_plural = 'User Storage'

    def __str__(self):
        return self.user.username
