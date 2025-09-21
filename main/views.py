from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from .forms import CustomAuthForm

def home(request):
    if request.user.is_authenticated:
        # Авторизованный пользователь - обычная главная
        return render(request, 'home.html')
    else:
        # Неавторизованный - страница факультетов
        faculties = [
            {
                'name': 'ВМК',
                'full_name': 'Факультет вычислительной математики и кибернетики',
                'description': 'Ведущий факультет в области computer science...',
                'points': 95,
                'website': 'https://cs.msu.ru'
            },
            # ... другие факультеты
        ]
        return render(request, 'faculties.html', {'faculties': faculties})

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = CustomAuthForm()
    return render(request, 'login.html', {'form': form})

@login_required
def profile(request):
    return render(request, 'profile.html')