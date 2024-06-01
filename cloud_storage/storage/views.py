import os
import logging

from django.http import HttpResponse, Http404
from django.middleware.csrf import get_token
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import action, api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .forms import CustomUserCreationForm
from .models import UserStorage, StorageFiles
from .serializers import UserSerializer, StorageFilesSerializer


logger = logging.getLogger(__name__)

@api_view(['GET'])
def csrf_token_view(request):
    return Response({'csrfToken': get_token(request)})


@csrf_exempt
def custom_register(request):
    ''' регистрация пользователя '''
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = CustomUserCreationForm()
    context = {
        'form':form
    }
    return render(request, 'register.html', context)


class UserViewSet(ModelViewSet):
    '''Работа с профилями пользователей'''
    permission_classes = [IsAdminUser]
    queryset = UserStorage.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination


class StorageFilesViewSet(ModelViewSet):
    queryset = StorageFiles.objects.all()
    serializer_class = StorageFilesSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        logger.debug(f"{self.__class__.__name__} user={user} request={self.request}")
        if user.is_superuser or user.is_staff:
            return StorageFiles.objects.all()
        return StorageFiles.objects.filter(owner=user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        serializer.save(owner=self.request.user)

    def create(self, request, *args, **kwargs):
        file = request.data.get('file', None)
        if file is None:
            return Response(
                {"detail": "File field cannot be null."},
                status=status.HTTP_400_BAD_REQUEST
            )
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

    @action(detail=False, methods=['get'], url_path='download/(?P<short_link>[^/.]+)')
    def download_by_short_link(self, request, short_link=None):
        try:
            file_record = StorageFiles.objects.get(short_link=short_link)
            file_record.last_download_date = timezone.now()
            file_record.save()

            file_path = file_record.file.path
            with open(file_path, 'rb') as file:
                response = HttpResponse(file.read(), content_type='application/octet-stream')
                response['Content-Disposition'] = f'attachment; filename={file_record.original_name}'
                return response
        except StorageFiles.DoesNotExist:
            raise Http404("File not found")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        file_path = instance.file.path
        if os.path.exists(file_path):
            os.remove(file_path)
        instance.delete()
