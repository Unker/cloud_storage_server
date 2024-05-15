from rest_framework import serializers

from storage.models import UserStorage


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserStorage
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'is_active',
            'is_staff',
            'is_superuser',
        ]
