from django import forms
from .models import Material, MaterialFolder
from django.core.exceptions import ValidationError
import os

ALLOWED_MATERIAL_EXTENSIONS = {
    '.pdf', '.png', '.jpg', '.jpeg', '.webp', '.gif',
    '.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx', '.txt', '.zip', '.rar'
}

MAX_MATERIAL_FILE_BYTES = 50 * 1024 * 1024  # 50 MB


class MaterialUploadForm(forms.ModelForm):
    new_folder = forms.CharField(
        required=False,
        label='Или создайте новую папку',
        widget=forms.TextInput(attrs={
            'placeholder': 'Введите название новой папки...',
            'class': 'form-control'
        })
    )

    class Meta:
        model = Material
        fields = ['name', 'file', 'faculty', 'course', 'subject', 'type', 'folder']
        widgets = {
            'faculty': forms.Select(choices=[
                ('ВМК', 'Факультет вычислительной математики и кибернетики'),
                ('Мехмат', 'Механико-математический факультет'),
                ('Физфак', 'Физический факультет'),
            ], attrs={'class': 'form-control'}),
            'course': forms.Select(choices=[(i, f'{i} курс') for i in range(1, 7)],
                                   attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'folder': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ограничиваем выбор папок только соответствующими факультету и курсу
        if 'faculty' in self.initial and 'course' in self.initial:
            self.fields['folder'].queryset = MaterialFolder.objects.filter(
                faculty=self.initial['faculty'],
                course=self.initial['course']
            )

    def clean_file(self):
        f = self.cleaned_data.get('file')
        if not f:
            return f
        ext = os.path.splitext(f.name)[1].lower()
        if ext not in ALLOWED_MATERIAL_EXTENSIONS:
            raise ValidationError('Недопустимый тип файла')
        if hasattr(f, 'size') and f.size and f.size > MAX_MATERIAL_FILE_BYTES:
            raise ValidationError('Файл слишком большой (лимит 50 МБ)')
        return f

class MaterialFilterForm(forms.Form):
    faculty = forms.ChoiceField(choices=[('', 'Все факультеты')] + [
        ('ВМК', 'ВМК'), ('Мехмат', 'Мехмат'), ('Физфак', 'Физфак')
    ], required=False)
    course = forms.ChoiceField(choices=[('', 'Все курсы')] + [
        (i, f'{i} курс') for i in range(1, 7)
    ], required=False)
    subject = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Предмет'}))
    material_type = forms.ChoiceField(choices=[('', 'Все типы')] + Material.TYPES, required=False)


class MaterialEditForm(forms.ModelForm):
    replace_file = forms.BooleanField(required=False, initial=False, label='Заменить файл')

    class Meta:
        model = Material
        fields = ['name', 'type', 'file']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        # if replace_file not checked, keep old file
        if not self.cleaned_data.get('replace_file'):
            self.fields['file'].required = False
            if 'file' in self.changed_data:
                instance.file = self.instance.file
        if commit:
            instance.save()
        return instance

    def clean_file(self):
        f = self.cleaned_data.get('file')
        # Allow empty if not replacing
        if not f:
            return f
        ext = os.path.splitext(f.name)[1].lower()
        if ext not in ALLOWED_MATERIAL_EXTENSIONS:
            raise ValidationError('Недопустимый тип файла')
        if hasattr(f, 'size') and f.size and f.size > MAX_MATERIAL_FILE_BYTES:
            raise ValidationError('Файл слишком большой (лимит 50 МБ)')
        return f