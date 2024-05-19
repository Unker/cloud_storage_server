import os

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

from .models import UserStorage
from cloud_storage.settings import STORAGE_PATH


class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(label='username', min_length=5, max_length=150)
    first_name = forms.CharField(label='First name', min_length=5, max_length=150)
    last_name = forms.CharField(label='Last name', min_length=5, max_length=150)
    email = forms.EmailField(label='email')
    password1 = forms.CharField(label='password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput)

    field_order = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

    class Meta:
        model = UserStorage
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def clean_username(self):
        username = self.cleaned_data['username'].lower()
        new = UserStorage.objects.filter(username=username)
        if new.count():
            raise ValidationError("User Already Exist")
        return username

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        new = UserStorage.objects.filter(email=email)
        if new.count():
            raise ValidationError(" Email Already Exist")
        return email

    def clean_password2(self):
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']

        if password1 and password2 and password1 != password2:
            raise ValidationError("Password don't match")
        return password2

    def save(self, commit=True):
        # создадим каталог хранилища пользователя
        user_storage_path = os.path.join(STORAGE_PATH, self.cleaned_data['username'])
        os.makedirs(user_storage_path, exist_ok=True)

        # создадим пользователя
        user = UserStorage.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password1'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            storage_path=user_storage_path,
        )

        return user
