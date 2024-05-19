from django.contrib import admin

from .models import UserStorage, StorageFiles


@admin.register(UserStorage)
class UserStorageAdmin(admin.ModelAdmin):
    list_display = (
        "username",
        "storage_path",
        "last_login",
        "is_superuser",
        "is_staff",
        "is_active",
        "email",
        "first_name",
        "last_name",
    )

@admin.register(StorageFiles)
class StorageFilesViewSetAdmin(admin.ModelAdmin):
    pass