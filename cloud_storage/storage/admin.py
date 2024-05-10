from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import UserStorage


class UserStorageInline(admin.StackedInline):
    model = UserStorage
    can_delete = False
    verbose_name_plural = "User Storage"

class CustomUserAdmin(UserAdmin):
    inlines = [UserStorageInline]

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(UserStorage)
class UserStorageAdmin(admin.ModelAdmin):
    list_display = ("get_username", "storage_path",)

    def get_username(self, obj):
        return obj.user.username

    get_username.short_description = "Username"