from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, FileResponse
from django.utils import timezone
from datetime import datetime, timedelta, date
from .models import Schedule, Subject
from .forms import HomeworkForm


def is_headman_or_above(user):
    return user.role in ['headman', 'teacher', 'admin']


@login_required
def schedule_view(request):
    user_group = request.user.group

    if not user_group:
        context = {
            'schedule': [],
            'week_dates': [],
            'current_date': date.today(),
            'error': '❌ У вас не назначена группа. Обратитесь к администратору.'
        }
        return render(request, 'schedule.html', context)

    # Получаем дату из параметра или текущую дату
    current_date_str = request.GET.get('date', date.today().isoformat())
    try:
        current_date = datetime.strptime(current_date_str, '%Y-%m-%d').date()
    except ValueError:
        current_date = date.today()

    # Вычисляем даты недели
    start_of_week = current_date - timedelta(days=current_date.weekday())
    week_dates = [start_of_week + timedelta(days=i) for i in range(7)]

    # Даты для навигации
    previous_week = (current_date - timedelta(days=7)).isoformat()
    next_week = (current_date + timedelta(days=7)).isoformat()

    # Получаем день недели для текущей даты
    days_map = {
        0: 'monday', 1: 'tuesday', 2: 'wednesday',
        3: 'thursday', 4: 'friday', 5: 'saturday'
    }
    current_day = days_map.get(current_date.weekday(), 'monday')

    # Расписание на текущий день
    schedule = Schedule.objects.filter(
        group=user_group,
        day=current_day
    ).order_by('lesson_number')

    context = {
        'schedule': schedule,
        'week_dates': week_dates,
        'current_date': current_date,
        'current_date_str': current_date.isoformat(),
        'previous_week': previous_week,
        'next_week': next_week,
    }
    return render(request, 'schedule.html', context)


@login_required
def day_schedule(request, day):
    """Старая функция для обратной совместимости - перенаправляет на новую систему с датами"""
    # Маппинг старых названий дней на даты текущей недели
    day_mapping = {
        'monday': 0, 'tuesday': 1, 'wednesday': 2,
        'thursday': 3, 'friday': 4, 'saturday': 5
    }

    if day not in day_mapping:
        return redirect('schedule')

    # Вычисляем дату для запрошенного дня
    today = date.today()
    days_difference = day_mapping[day] - today.weekday()
    target_date = today + timedelta(days=days_difference)

    return redirect(f'/schedule/?date={target_date.isoformat()}')


@login_required
@user_passes_test(is_headman_or_above)
def add_homework(request, schedule_id):
    schedule_item = get_object_or_404(Schedule, id=schedule_id)

    user = request.user
    if user.role == 'headman' and schedule_item.group != user.group:
        messages.error(request, "Вы можете добавлять ДЗ только для своей группы")
        return redirect('schedule')

    if user.role == 'teacher' and schedule_item.subject.teacher != user:
        messages.error(request, "Вы можете добавлять ДЗ только для своих предметов")
        return redirect('schedule')

    if request.method == 'POST':
        form = HomeworkForm(request.POST, request.FILES, instance=schedule_item)
        if form.is_valid():
            form.save()
            messages.success(request, "Домашнее задание успешно сохранено")
            return redirect('schedule')
    else:
        form = HomeworkForm(instance=schedule_item)

    context = {
        'form': form,
        'schedule_item': schedule_item
    }
    return render(request, 'add_homework.html', context)


@login_required
def download_homework_file(request, schedule_id):
    schedule_item = get_object_or_404(Schedule, id=schedule_id)
    if schedule_item.homework_file:
        response = FileResponse(schedule_item.homework_file.open(), as_attachment=True)
        response['Content-Disposition'] = f'attachment; filename="{schedule_item.homework_file.name}"'
        return response
    else:
        messages.error(request, "Файл не найден")
        return redirect('schedule')


@login_required
def schedule_json(request, day=None):
    user_group = request.user.group

    if not user_group:
        return JsonResponse({'error': 'Group not assigned'}, status=400)

    if day:
        schedule = Schedule.objects.filter(group=user_group, day=day)
    else:
        schedule = Schedule.objects.filter(group=user_group)

    schedule_data = []
    for item in schedule.order_by('day', 'lesson_number'):
        schedule_data.append({
            'day': item.get_day_display(),
            'lesson_number': item.lesson_number,
            'time': item.time,
            'subject': item.subject.name,
            'teacher': item.subject.teacher.get_full_name(),
            'classroom': item.classroom,
            'homework': item.homework,
            'homework_file': item.homework_file.url if item.homework_file else None,
            'homework_date': item.homework_date.isoformat() if item.homework_date else None
        })

    return JsonResponse({'schedule': schedule_data})


@login_required
def download_homework_file(request, schedule_id):
    schedule_item = get_object_or_404(Schedule, id=schedule_id)
    if schedule_item.homework_file:
        response = FileResponse(schedule_item.homework_file.open(), as_attachment=True)
        response['Content-Disposition'] = f'attachment; filename="{schedule_item.homework_file.name}"'
        return response
    else:
        messages.error(request, "Файл не найден")
        return redirect('schedule')


@login_required
def schedule_json(request, day=None):
    user_group = request.user.group

    if not user_group:
        return JsonResponse({'error': 'Group not assigned'}, status=400)

    if day:
        schedule = Schedule.objects.filter(group=user_group, day=day)
    else:
        schedule = Schedule.objects.filter(group=user_group)

    schedule_data = []
    for item in schedule.order_by('day', 'lesson_number'):
        schedule_data.append({
            'day': item.get_day_display(),
            'lesson_number': item.lesson_number,
            'time': item.time,
            'subject': item.subject.name,
            'teacher': item.subject.teacher.get_full_name(),
            'classroom': item.classroom,
            'homework': item.homework,
            'homework_file': item.homework_file.url if item.homework_file else None,
            'homework_date': item.homework_date.isoformat() if item.homework_date else None
        })

    return JsonResponse({'schedule': schedule_data})