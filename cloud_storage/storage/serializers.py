from rest_framework import serializers

from storage.models import UserStorage, StorageFiles


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserStorage
        fields = [
            'id',
            'email',
            'username',
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
        read_only_fields = [
            'owner',
            'original_name',
            'size',
            'upload_date',
            'last_update_date',
            'last_download_date',
            'short_link',
        ]

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data['owner'] = instance.owner
        return super().update(instance, validated_data)