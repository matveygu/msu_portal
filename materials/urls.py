from django.urls import path
from . import views

urlpatterns = [
    # Главная страница материалов
    path('', views.materials_view, name='materials'),

    # Материалы по факультету
    path('<str:faculty>/', views.faculty_materials, name='faculty_materials'),

    # Материалы по курсу
    path('<str:faculty>/<int:course>/', views.course_materials, name='course_materials'),

    # Материалы по предмету
    path('<str:faculty>/<int:course>/<str:subject>/', views.subject_materials, name='subject_materials'),

    # Материалы по типу
    path('<str:faculty>/<int:course>/<str:subject>/<str:material_type>/',
         views.type_materials, name='type_materials'),

    # Загрузка материала
    path('upload/', views.upload_material, name='upload_material'),

    # Скачивание материала
    path('download/<int:material_id>/', views.download_material, name='download_material'),
]