from django_filters import CharFilter, FilterSet, ChoiceFilter, DateFilter
from django.contrib.auth.models import User
from django import forms
from .models import Task


class EmployeeFilter(FilterSet):
    username = CharFilter(field_name='username', lookup_expr='icontains')

    class Meta:
        model = User
        fields = ['username']


class TaskFilter(FilterSet):
    name = CharFilter(
        field_name='name',
        lookup_expr='icontains',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control-sm w-50',
                'autocomplete': 'off',
                'spellcheck': "false"
            }
        )
    )
    status = ChoiceFilter(
        choices=(
            ('new', 'new'),
            ('processing', 'processing'),
            ('done', 'done')
        ),
        field_name='status',
        widget=forms.Select(
            attrs={
                'class': 'form-control-sm w-50'
            }
        )
    )
    note = CharFilter(
        field_name='note',
        lookup_expr='icontains',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control-sm w-50',
                'autocomplete': 'off',
                'spellcheck': "false"
            }
        )
    )
    date_given = DateFilter(
        field_name='date_given',
        lookup_expr='icontains',
        widget=forms.DateTimeInput(
            attrs={
                'class': 'form-control-sm w-50',
                'spellcheck': "false"
            }
        )
    )
    deadline = DateFilter(
        field_name='deadline',
        lookup_expr='icontains',
        widget=forms.DateTimeInput(
            attrs={
                'class': 'form-control-sm w-50',
                'spellcheck': "false"
            }
        )
    )

    class Meta:
        model = Task
        fields = ['name', 'date_given', 'deadline', 'status', 'note']
