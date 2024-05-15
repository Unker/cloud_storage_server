from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .forms import CustomUserCreationForm
from .models import UserStorage
from .serializers import UserSerializer


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
