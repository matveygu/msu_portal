from django.db import models
from main.models import Group, CustomUser
from datetime import date


class Subject(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название предмета')
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'teacher'})

    def __str__(self):
        return self.name


class Homework(models.Model):
    """Отдельная модель для домашних заданий, привязанных к датам"""
    schedule = models.ForeignKey('Schedule', on_delete=models.CASCADE, related_name='homework_assignments')
    content = models.TextField(verbose_name='Текст задания')
    file = models.FileField(upload_to='homework/%Y/%m/%d/', blank=True, null=True, verbose_name='Файл задания')
    assigned_date = models.DateField(default=date.today, verbose_name='Дата задания')
    due_date = models.DateField(blank=True, null=True, verbose_name='Срок сдачи')
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='Кем задано')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')

    class Meta:
        ordering = ['-assigned_date']
        verbose_name = 'Домашнее задание'
        verbose_name_plural = 'Домашние задания'

    def __str__(self):
        return f"ДЗ для {self.schedule} от {self.assigned_date}"


class Schedule(models.Model):
    DAYS = [
        ('monday', 'Понедельник'),
        ('tuesday', 'Вторник'),
        ('wednesday', 'Среда'),
        ('thursday', 'Четверг'),
        ('friday', 'Пятница'),
        ('saturday', 'Суббота'),
    ]

    group = models.ForeignKey(Group, on_delete=models.CASCADE, verbose_name='Группа')
    day = models.CharField(max_length=15, choices=DAYS, verbose_name='День недели')
    lesson_number = models.IntegerField(verbose_name='Номер пары')
    time = models.CharField(max_length=20, verbose_name='Время')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name='Предмет')
    classroom = models.CharField(max_length=50, verbose_name='Аудитория')

    class Meta:
        ordering = ['day', 'lesson_number']
        verbose_name = 'Расписание'
        verbose_name_plural = 'Расписание'

    def __str__(self):
        return f"{self.group} - {self.get_day_display()} - {self.lesson_number} пара"

    def get_homework_for_date(self, target_date):
        """Получить ДЗ для конкретной даты"""
        return self.homework_assignments.filter(assigned_date=target_date).first()