from django.core.checks import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, FileResponse
from django.conf import settings
import os
from .models import Material, MaterialFolder
from .forms import MaterialUploadForm


def is_headman_or_above(user):
    return user.role in ['headman', 'teacher', 'admin']


@login_required
def materials_view(request):
    # Получаем все уникальные факультеты и курсы для навигации
    faculties = Material.objects.values_list('faculty', flat=True).distinct()
    courses = Material.objects.values_list('course', flat=True).distinct()

    # Показываем материалы для факультета пользователя по умолчанию
    user_faculty = request.user.faculty
    materials = Material.objects.filter(faculty=user_faculty)

    context = {
        'materials': materials,
        'faculties': faculties,
        'courses': courses,
        'current_faculty': user_faculty,
    }
    return render(request, 'materials.html', context)


@login_required
def faculty_materials(request, faculty):
    courses = Material.objects.filter(faculty=faculty).values_list('course', flat=True).distinct()
    materials = Material.objects.filter(faculty=faculty)

    context = {
        'materials': materials,
        'faculties': Material.objects.values_list('faculty', flat=True).distinct(),
        'courses': courses,
        'current_faculty': faculty,
    }
    return render(request, 'materials.html', context)


@login_required
def course_materials(request, faculty, course):
    subjects = Material.objects.filter(faculty=faculty, course=course).values_list('subject', flat=True).distinct()
    materials = Material.objects.filter(faculty=faculty, course=course)

    context = {
        'materials': materials,
        'faculties': Material.objects.values_list('faculty', flat=True).distinct(),
        'courses': Material.objects.values_list('course', flat=True).distinct(),
        'subjects': subjects,
        'current_faculty': faculty,
        'current_course': course,
    }
    return render(request, 'materials.html', context)


@login_required
def subject_materials(request, faculty, course, subject):
    material_types = Material.objects.filter(
        faculty=faculty,
        course=course,
        subject=subject
    ).values_list('type', flat=True).distinct()

    materials = Material.objects.filter(
        faculty=faculty,
        course=course,
        subject=subject
    )

    context = {
        'materials': materials,
        'current_faculty': faculty,
        'current_course': course,
        'current_subject': subject,
        'material_types': material_types,
    }
    return render(request, 'materials.html', context)


@login_required
def type_materials(request, faculty, course, subject, material_type):
    materials = Material.objects.filter(
        faculty=faculty,
        course=course,
        subject=subject,
        type=material_type
    )

    context = {
        'materials': materials,
        'current_faculty': faculty,
        'current_course': course,
        'current_subject': subject,
        'current_type': material_type,
    }
    return render(request, 'materials.html', context)


@login_required
@user_passes_test(is_headman_or_above)
def upload_material(request):
    if request.method == 'POST':
        form = MaterialUploadForm(request.POST, request.FILES)
        if form.is_valid():
            material = form.save(commit=False)
            material.uploaded_by = request.user

            # Создаем папку если указана новая
            folder_name = request.POST.get('new_folder', '').strip()
            if folder_name:
                folder, created = MaterialFolder.objects.get_or_create(
                    name=folder_name,
                    faculty=material.faculty,
                    course=material.course,
                    subject=material.subject,
                    defaults={
                        'created_by': request.user
                    }
                )
                material.folder = folder

            material.save()
            messages.success(request, "Материал успешно загружен")
            return redirect('materials')
    else:
        form = MaterialUploadForm(initial={
            'faculty': request.user.faculty,
            'course': request.user.course
        })

    # Получаем доступные папки для выбора
    folders = MaterialFolder.objects.filter(
        faculty=request.user.faculty,
        course=request.user.course
    )

    context = {
        'form': form,
        'folders': folders
    }
    return render(request, 'upload.html', context)


@login_required
def download_material(request, material_id):
    material = get_object_or_404(Material, id=material_id)
    file_path = os.path.join(settings.MEDIA_ROOT, str(material.file))

    if os.path.exists(file_path):
        response = FileResponse(open(file_path, 'rb'))
        response['Content-Disposition'] = f'attachment; filename="{material.file.name}"'
        return response
    else:
        return HttpResponse("Файл не найден", status=404)