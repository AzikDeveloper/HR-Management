from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import Task


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
            'password1',
            'password2'
        ]


class CreateTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = '__all__'
        exclude = ['date_given']
        widgets = {
            'assigned_to': forms.Select(
                attrs={
                    'class': 'form-control w-50',
                    'disabled': ''
                }
            ),
            'name': forms.TextInput(
                attrs={
                    'class': 'form-control w-50'
                }
            ),
            'context': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 5,
                }
            ),
            'status': forms.Select(
                attrs={
                    'class': 'form-control w-50',
                }
            ),
            'deadline': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control w-25'
                }
            ),
        }
