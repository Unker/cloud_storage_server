import os
import logging

from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action, api_view
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .forms import CustomUserCreationForm
from .models import UserStorage, StorageFiles
from .serializers import UserSerializer, StorageFilesSerializer
from .decorators import handle_file_download

logger = logging.getLogger(__name__)


@csrf_exempt
@api_view(['GET'])
def csrf_token_view(request):
    return Response({'csrfToken': get_token(request)})


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super(CustomAuthToken, self).post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        user = token.user
        return Response({
            'token': token.key,
            'user_id': user.id,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'username': user.username,
        })
@csrf_exempt
def custom_register(request):
    """ регистрация пользователя """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success', 'message': 'User registered successfully'})
        else:
            errors = form.errors.as_json()
            return JsonResponse({'status': 'error', 'errors': errors}, status=400)
    else:
        form = CustomUserCreationForm()
        context = {
            'form': form
        }
        return render(request, 'register.html', context)


class UserViewSet(ModelViewSet):
    """Работа с профилями пользователей"""
    permission_classes = [IsAdminUser]
    queryset = UserStorage.objects.all()
    serializer_class = UserSerializer
    pagination_class = LimitOffsetPagination


class StorageFilesViewSet(ModelViewSet):
    queryset = StorageFiles.objects.all()
    serializer_class = StorageFilesSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    def get_queryset(self):
        user = self.request.user
        logger.debug(f"{self.__class__.__name__} user={user} request={self.request}")
        if (self.request.method not in SAFE_METHODS) and (user.is_superuser or user.is_staff):
            return StorageFiles.objects.all()
        return StorageFiles.objects.filter(owner=user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        serializer.save(owner=self.request.user)

    def create(self, request, *args, **kwargs):
        user = self.request.user
        logger.debug(f"{self.__class__.__name__} Start file upload by user={user} request={self.request}")
        file = request.data.get('file', None)
        if file is None:
            logger.error(f"{self.__class__.__name__} File field is null by user={user} request={self.request}")
            return Response(
                {"detail": "File field cannot be null."},
                status=status.HTTP_400_BAD_REQUEST
            )
        logger.debug(f"{self.__class__.__name__} File uploaded: {file.name} by user={user} request={self.request}")
        return super().create(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def by_user(self, request, pk=None):
        # маршрут будет доступен по URL-пути storagefiles/by_user/?user_id=1
        if not request.user.is_staff and not request.user.is_superuser:
            return redirect('/')

        user_id = request.query_params.get('user_id')
        if user_id:
            files = StorageFiles.objects.filter(owner_id=user_id)
            page = self.paginate_queryset(files)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = self.get_serializer(files, many=True)
            return Response(serializer.data)
        else:
            return Response({"detail": "user_id parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def generate_short_link(self, request, pk=None):
        # эндпоинт /storagefiles/<id>/generate_short_link/
        file = self.get_object()
        file.generate_short_link()
        return Response({'short_link': file.short_link}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def delete_short_link(self, request, pk=None):
        # эндпоинт /storagefiles/<id>/delete_short_link/
        file = self.get_object()
        file.delete_short_link()
        return Response({'short_link': file.short_link}, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['get'],
        url_path='download/(?P<short_link>[^/.]+)',
        permission_classes=[AllowAny],
    )
    @handle_file_download
    def download_by_short_link(self, request, short_link=None):
        """This function downloads a file by short_link"""
        return StorageFiles.objects.get(short_link=short_link)

    @action(detail=True, methods=['get'], url_path='download')
    @handle_file_download
    def download_by_id(self, request, pk=None):
        """This function downloads a file by ID"""
        return get_object_or_404(StorageFiles, pk=pk)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        file_path = instance.file.path
        if os.path.exists(file_path):
            os.remove(file_path)
        instance.delete()

    def has_permission_to_download(self, user, file_instance):
        # Проверка прав доступа: разрешить только администратору или владельцу файла
        return user.is_superuser or user.is_staff or user == file_instance.owner
