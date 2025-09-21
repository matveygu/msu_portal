from django.db import models
from main.models import Group, CustomUser


class MaterialFolder(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название папки')
    faculty = models.CharField(max_length=100, verbose_name='Факультет')
    course = models.IntegerField(verbose_name='Курс')
    subject = models.CharField(max_length=100, verbose_name='Предмет', blank=True)
    parent_folder = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                                      verbose_name='Родительская папка')
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='Создатель')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Папка материалов'
        verbose_name_plural = 'Папки материалов'
        ordering = ['faculty', 'course', 'subject', 'name']

    def __str__(self):
        path = f"{self.faculty}/{self.course} курс"
        if self.subject:
            path += f"/{self.subject}"
        if self.parent_folder:
            path += f"/{self.parent_folder.name}"
        return f"{path}/{self.name}"


class Material(models.Model):
    TYPES = [
        ('book', 'Книга'),
        ('notes', 'Конспект'),
        ('video', 'Видео'),
        ('presentation', 'Презентация'),
        ('code', 'Исходный код'),
        ('other', 'Другое'),
    ]

    name = models.CharField(max_length=200, verbose_name='Название')
    file = models.FileField(upload_to='materials/', verbose_name='Файл')
    faculty = models.CharField(max_length=100, verbose_name='Факультет')
    course = models.IntegerField(verbose_name='Курс')
    subject = models.CharField(max_length=100, verbose_name='Предмет')
    type = models.CharField(max_length=20, choices=TYPES, verbose_name='Тип материала')
    folder = models.ForeignKey(MaterialFolder, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Папка')
    uploaded_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='Загрузил')
    upload_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата загрузки')

    class Meta:
        verbose_name = 'Материал'
        verbose_name_plural = 'Материалы'
        ordering = ['-upload_date']

    def __str__(self):
        return self.name