from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .forms import CustomUserCreationForm

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
