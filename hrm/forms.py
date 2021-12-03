from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django import forms
from .models import Task, Info, GenLink
from .validators import NameValidator
import re


class RegisterUserForm(UserCreationForm):
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

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        if re.match("^(?=[a-zA-Z0-9._]{5,20}$)(?!.*[_.]{2})[^_.].*[^_.]$", username):
            return username
        else:
            raise ValidationError('invalid username')

    def clean_first_name(self):
        first_name = self.cleaned_data['first_name']
        first_name_validator = NameValidator(first_name, 'first')
        if first_name_validator.is_valid:
            return first_name_validator.cleaned_name
        else:
            raise ValidationError(first_name_validator.error_message)

    def clean_last_name(self):
        last_name = self.cleaned_data['last_name']
        last_name_validator = NameValidator(last_name, 'last')
        if last_name_validator.is_valid:
            return last_name_validator.cleaned_name
        else:
            raise ValidationError(last_name_validator.error_message)


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email']


class CreatePreUserForm:
    def __init__(self, username, email, section, group):
        self.is_success = False
        self.error_message = ''
        user = User.objects.filter(username=username)
        if user:
            self.is_success = False
            self.error_message = 'A user with this username already exists'
        else:
            user = User(username=username, email=email)
            user._section = section
            user._group = group
            user.save()
            self.is_success = True

    def is_created(self):
        return self.is_success


class CreateTaskForm(forms.ModelForm):

    class Meta:
        model = Task
        fields = '__all__'
        exclude = ['date_given']
