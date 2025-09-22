import json
import os
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .forms import CustomAuthForm


def load_faculties_from_json():
    """Загружает данные о факультетах из JSON файла"""
    json_path = os.path.join(settings.BASE_DIR, 'static', 'data', 'faculties.json')

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            faculties = data.get('faculties', [])

            # Добавляем пути к локальным логотипам
            for faculty in faculties:
                # Формируем путь к локальному файлу логотипа
                logo_filename = f"{faculty['name'].lower()}.png"
                logo_path = f"images/faculties/{logo_filename}"

                # Проверяем существует ли файл
                full_logo_path = os.path.join(settings.BASE_DIR, 'static', logo_path)
                if os.path.exists(full_logo_path):
                    faculty['local_logo'] = logo_path
                else:
                    faculty['local_logo'] = None

            return faculties
    except FileNotFoundError:
        return get_default_faculties()
    except Exception as e:
        print(f"Ошибка загрузки JSON: {e}")
        return get_default_faculties()


def get_default_faculties():
    """Возвращает тестовые данные с локальными логотипами"""
    return [
        {
            'id': 1,
            'name': 'ВМК',
            'full_name': 'Факультет вычислительной математики и кибернетики',
            'description': 'Ведущий факультет в области computer science в России. Готовит специалистов в области программирования, искусственного интеллекта, анализа данных и кибербезопасности.',
            'points': 424,
            'max_points': 500,
            'previous_points': 414,
            'website': 'https://cs.msu.ru',
            'contact': 'vmk@cs.msu.ru',
            'phone': '+7 (495) 939-54-01',
            'local_logo': 'data/faculties/vmk.png'
        }
    ]


def home(request):
    if request.user.is_authenticated:
        return render(request, 'home.html')
    else:
        faculties = load_faculties_from_json()
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