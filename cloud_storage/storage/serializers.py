from rest_framework import serializers

from storage.models import UserStorage, StorageFiles


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

class StorageFilesSerializer(serializers.ModelSerializer):
    class Meta:
        model = StorageFiles
        fields = '__all__'
        read_only_fields = ['size', 'upload_date', 'last_update_date', 'short_link']