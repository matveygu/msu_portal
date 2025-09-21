from django import forms
from .models import Homework

class HomeworkForm(forms.ModelForm):
    class Meta:
        model = Homework
        fields = ['content', 'file', 'assigned_date', 'due_date']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': 'Введите домашнее задание...'
            }),
            'assigned_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'due_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
        }
        labels = {
            'content': 'Домашнее задание',
            'file': 'Файл задания',
            'assigned_date': 'Дата задания',
            'due_date': 'Срок сдачи'
        }