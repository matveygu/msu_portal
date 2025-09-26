import json
import os
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings
from .forms import CustomAuthForm
from django.core.paginator import Paginator
from datetime import datetime, timedelta, date
from .models import News
from django.contrib import messages
from .forms import NewsForm
from schedule.models import Schedule


def is_teacher_or_above(user):
    return user.role in ['teacher', 'admin']


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
        # Получаем расписание на сегодня для текущего пользователя
        today_schedule = []
        if hasattr(request.user, 'group') and request.user.group:
            # Получаем день недели для сегодня
            days_map = {
                0: 'monday', 1: 'tuesday', 2: 'wednesday',
                3: 'thursday', 4: 'friday', 5: 'saturday'
            }
            today = date.today()
            today_day = days_map.get(today.weekday(), 'monday')

            # Получаем расписание на сегодня
            today_schedule = Schedule.objects.filter(
                group=request.user.group,
                day=today_day
            ).order_by('lesson_number')

        # Получаем новости с пагинацией
        news_list = News.objects.filter(is_published=True).order_by('-created_at')
        paginator = Paginator(news_list, 5)  # 5 новостей на страницу
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'today_schedule': today_schedule,
            'page_obj': page_obj,
            'today': date.today(),
        }
        return render(request, 'home.html', context)
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


@login_required
@user_passes_test(is_teacher_or_above)
def add_news(request):
    """Добавление новости"""
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES)
        if form.is_valid():
            news = form.save(commit=False)
            news.author = request.user
            news.save()
            messages.success(request, 'Новость успешно добавлена')
            return redirect('home')
    else:
        form = NewsForm()

    return render(request, 'add_news.html', {'form': form})


@login_required
@user_passes_test(is_teacher_or_above)
def edit_news(request, news_id):
    """Редактирование новости"""
    news = get_object_or_404(News, id=news_id)

    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES, instance=news)
        if form.is_valid():
            form.save()
            messages.success(request, 'Новость успешно обновлена')
            return redirect('home')
    else:
        form = NewsForm(instance=news)

    return render(request, 'edit_news.html', {'form': form, 'news': news})


@login_required
@user_passes_test(is_teacher_or_above)
def delete_news(request, news_id):
    """Удаление новости"""
    news = get_object_or_404(News, id=news_id)
    if request.method == 'POST':
        news.delete()
        messages.success(request, 'Новость успешно удалена')
    return redirect('home')