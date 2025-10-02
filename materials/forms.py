from django import forms
from .models import Material, MaterialFolder


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

class MaterialFilterForm(forms.Form):
    faculty = forms.ChoiceField(choices=[('', 'Все факультеты')] + [
        ('ВМК', 'ВМК'), ('Мехмат', 'Мехмат'), ('Физфак', 'Физфак')
    ], required=False)
    course = forms.ChoiceField(choices=[('', 'Все курсы')] + [
        (i, f'{i} курс') for i in range(1, 7)
    ], required=False)
    subject = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Предмет'}))
    material_type = forms.ChoiceField(choices=[('', 'Все типы')] + Material.TYPES, required=False)