"""
URL configuration for cloud_storage project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token

from storage.views import custom_register, csrf_token_view

from storage.views import UserViewSet, StorageFilesViewSet


router = routers.DefaultRouter()
router.register(r'users', UserViewSet, basename="users")
router.register(r'storagefiles', StorageFilesViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path("admin/", admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),

    path('accounts/register/', custom_register, name='custom_register'),

    # эндпоинт для получения токенов
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path('api/csrf/', csrf_token_view, name='api-csrf'),

    path('storagefiles/by_user/', StorageFilesViewSet.as_view({'get': 'by_user'}), name='storagefiles-by-user'),
    path('storagefiles/<int:pk>/generate_short_link/', StorageFilesViewSet.as_view({'post': 'generate_short_link'}),
         name='storagefiles-generate-short-link'),
]
