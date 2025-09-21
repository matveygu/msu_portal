#!/usr/bin/env python
import os
import sys
import django

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'msu_portal.settings')
django.setup()

from main.models import CustomUser, Group


def create_test_data():
    """Создает тестовые группы и пользователей"""

    print("🚀 Создание тестовых данных...")

    # 1. Создаем группы
    groups_data = [
        {"name": "ВМК-101", "faculty": "ВМК", "course": 1},
        {"name": "ВМК-102", "faculty": "ВМК", "course": 1},
        {"name": "ВМК-201", "faculty": "ВМК", "course": 2},
        {"name": "ВМК-202", "faculty": "ВМК", "course": 2},
        {"name": "ВМК-301", "faculty": "ВМК", "course": 3},
    ]

    groups = {}
    for group_data in groups_data:
        group, created = Group.objects.get_or_create(**group_data)
        groups[group.name] = group
        if created:
            print(f"✅ Создана группа: {group}")
        else:
            print(f"⚠️  Группа уже существует: {group}")

    # 2. Создаем тестовых пользователей
    test_users = [
        # Администраторы
        {
            "username": "admin",
            "password": "admin123",
            "student_id": "admin001",
            "first_name": "Алексей",
            "last_name": "Администраторов",
            "faculty": "ВМК",
            "course": 0,
            "role": "admin",
            "group": None
        },

        # Преподаватели
        {
            "username": "teacher1",
            "password": "teacher123",
            "student_id": "t0001",
            "first_name": "Сергей",
            "last_name": "Преподавателев",
            "faculty": "ВМК",
            "course": 0,
            "role": "teacher",
            "group": None
        },
        {
            "username": "teacher2",
            "password": "teacher123",
            "student_id": "t0002",
            "first_name": "Мария",
            "last_name": "Учителева",
            "faculty": "ВМК",
            "course": 0,
            "role": "teacher",
            "group": None
        },

        # Старосты
        {
            "username": "headman1",
            "password": "headman123",
            "student_id": "100001",
            "first_name": "Иван",
            "last_name": "Старостин",
            "faculty": "ВМК",
            "course": 1,
            "role": "headman",
            "group": groups["ВМК-101"]
        },
        {
            "username": "headman2",
            "password": "headman123",
            "student_id": "200001",
            "first_name": "Ольга",
            "last_name": "Старостина",
            "faculty": "ВМК",
            "course": 2,
            "role": "headman",
            "group": groups["ВМК-201"]
        },

        # Студенты 1 курс
        {
            "username": "student101",
            "password": "student123",
            "student_id": "101001",
            "first_name": "Анна",
            "last_name": "Иванова",
            "faculty": "ВМК",
            "course": 1,
            "role": "student",
            "group": groups["ВМК-101"]
        },
        {
            "username": "student102",
            "password": "student123",
            "student_id": "101002",
            "first_name": "Петр",
            "last_name": "Петров",
            "faculty": "ВМК",
            "course": 1,
            "role": "student",
            "group": groups["ВМК-101"]
        },
        {
            "username": "student103",
            "password": "student123",
            "student_id": "102001",
            "first_name": "Мария",
            "last_name": "Сидорова",
            "faculty": "ВМК",
            "course": 1,
            "role": "student",
            "group": groups["ВМК-102"]
        },

        # Студенты 2 курс
        {
            "username": "student201",
            "password": "student123",
            "student_id": "201001",
            "first_name": "Дмитрий",
            "last_name": "Кузнецов",
            "faculty": "ВМК",
            "course": 2,
            "role": "student",
            "group": groups["ВМК-201"]
        },
        {
            "username": "student202",
            "password": "student123",
            "student_id": "202001",
            "first_name": "Елена",
            "last_name": "Васильева",
            "faculty": "ВМК",
            "course": 2,
            "role": "student",
            "group": groups["ВМК-202"]
        },

        # Студенты 3 курс
        {
            "username": "student301",
            "password": "student123",
            "student_id": "301001",
            "first_name": "Александр",
            "last_name": "Смирнов",
            "faculty": "ВМК",
            "course": 3,
            "role": "student",
            "group": groups["ВМК-301"]
        }
    ]

    # Создаем пользователей
    for user_data in test_users:
        username = user_data['username']

        # Проверяем существует ли пользователь
        if CustomUser.objects.filter(username=username).exists():
            print(f"⚠️  Пользователь {username} уже существует, пропускаем")
            continue

        # Извлекаем пароль и группу
        password = user_data.pop('password')
        group = user_data.pop('group')

        try:
            # Создаем пользователя
            if user_data['role'] == 'admin':
                user = CustomUser.objects.create_superuser(**user_data)
            else:
                user = CustomUser.objects.create_user(**user_data)

            user.set_password(password)

            # Назначаем группу если указана
            if group:
                user.group = group

            user.save()

            print(f"✅ Создан: {user.username} ({user.get_role_display()}) - Группа: {user.group}")

        except Exception as e:
            print(f"❌ Ошибка при создании {username}: {e}")

    print("\n🎉 Тестовые данные созданы!")
    print("\n📋 Данные для входа:")
    print("Администратор: admin / admin123")
    print("Преподаватель: teacher1 / teacher123")
    print("Староста: headman1 / headman123")
    print("Студент: student101 / student123")
    print("\n📍 Адрес сайта: http://127.0.0.1:8000/")
    print("📍 Админка: http://127.0.0.1:8000/admin/")


if __name__ == "__main__":
    create_test_data()