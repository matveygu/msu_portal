#!/usr/bin/env python
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'msu_portal.settings')
django.setup()

from main.models import CustomUser, Group
from schedule.models import Subject, Schedule


def cleanup_duplicates():
    """Удаляет дубликаты групп"""
    print("🧹 Проверка дубликатов групп...")

    # Находим группы с одинаковыми именами
    from django.db.models import Count
    duplicates = Group.objects.values('name').annotate(
        count=Count('id')
    ).filter(count__gt=1)

    for item in duplicates:
        group_name = item['name']
        groups = Group.objects.filter(name=group_name)
        print(f"Найдено {len(groups)} групп с именем '{group_name}'")

        # Оставляем первую группу, удаляем остальные
        keep_group = groups.first()
        deleted_count = groups.exclude(id=keep_group.id).delete()[0]
        print(f"Удалено {deleted_count} дубликатов группы '{group_name}'")

    return len(duplicates)


def create_test_schedule():
    print("🚀 Создание тестового расписания...")

    # Очищаем дубликаты
    cleanup_duplicates()

    # 1. Преподаватель
    teacher, created = CustomUser.objects.get_or_create(
        username='teacher1',
        defaults={
            'student_id': 't0001',
            'first_name': 'Сергей',
            'last_name': 'Преподавателев',
            'faculty': 'ВМК',
            'course': 0,
            'role': 'teacher'
        }
    )
    if created:
        teacher.set_password('teacher123')
        teacher.save()
        print("✅ Преподаватель создан")
    else:
        print("⚠️ Преподаватель уже существует")

    # 2. Предмет
    subject, created = Subject.objects.get_or_create(
        name='Программирование',
        teacher=teacher
    )
    print("✅ Предмет создан" if created else "⚠️ Предмет уже существует")

    # 3. Группа (БЕЗОПАСНО с defaults)
    group, created = Group.objects.get_or_create(
        name='ВМК-101',
        defaults={
            'faculty': 'ВМК',
            'course': 1
        }
    )
    print("✅ Группа создана" if created else "✅ Группа уже существует")

    # 4. Расписание
    schedule_data = [
        {'day': 'Понедельник', 'number': 1, 'time': '9:00-10:30', 'classroom': '505'},
        {'day': 'Понедельник', 'number': 2, 'time': '10:45-12:15', 'classroom': '312'},
        {'day': 'Вторник', 'number': 1, 'time': '9:00-10:30', 'classroom': '411'},
        {'day': 'Среда', 'number': 1, 'time': '9:00-10:30', 'classroom': '505'},
    ]

    for data in schedule_data:
        schedule, created = Schedule.objects.get_or_create(
            group=group,
            day=data['day'],
            lesson_number=data['number'],
            teacher_id=teacher.student_id,
            defaults={
                'time': data['time'],
                'subject': subject,
                'classroom': data['classroom']
            }
        )
        status = "создана" if created else "уже существует"
        print(f"✅ Пара {data['number']} ({data['day']}) {status}")

    print("🎉 Тестовое расписание создано!")
    print("👤 Преподаватель: teacher1 / teacher123")
    print("📚 Предмет: Программирование")
    print("👥 Группа: ВМК-101")


if __name__ == "__main__":
    create_test_schedule()