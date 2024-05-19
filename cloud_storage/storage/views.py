from django.http import HttpResponse, Http404
from django.middleware.csrf import get_token
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import action, api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.utils import timezone
from rest_framework.viewsets import ModelViewSet

from .forms import CustomUserCreationForm
from .models import UserStorage, StorageFiles
from .serializers import UserSerializer, StorageFilesSerializer


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
        storage_user_id = self.request.query_params.get('user_id')

        if user.is_superuser and storage_user_id:
            return StorageFiles.objects.filter(owner_id=storage_user_id)
        return StorageFiles.objects.filter(owner=user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=False, methods=['get'])
    def by_user(self, request, pk=None):
        # маршрут будет доступен по URL-пути storagefiles/by_user/?user_id=1
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