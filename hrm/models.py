from django.db import models
from django.contrib.auth.models import User
import uuid


class Position(models.Model):
    name = models.CharField(max_length=50, null=True)

    def __str__(self):
        return self.name


class Director(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.user.username


class Section(models.Model):
    name = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.name


class Address(models.Model):
    street = models.CharField(max_length=200, null=True)
    state = models.CharField(max_length=200, null=True)
    city = models.CharField(max_length=200, null=True)
    zip_code = models.IntegerField(null=True)
    country = models.CharField(max_length=200, null=True)

    def __str__(self):
        return str(self.id)


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    username = models.CharField(max_length=200, null=True)
    first_name = models.CharField(max_length=200, null=True)
    last_name = models.CharField(max_length=200, null=True)
    salary = models.CharField(max_length=200, null=True)
    email = models.EmailField(max_length=200, null=True, blank=True)
    phone = models.CharField(max_length=200, null=True, blank=True)
    about = models.TextField(max_length=500, null=True, blank=True)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, related_name='employees_by_address', null=True)
    section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True, blank=True, related_name='employees_by_section')
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, related_name="employees_by_position", null=True)

    def __str__(self):
        try:
            return self.user.username
        except Exception:
            return f'employee-{self.id}'

    def save(self, *args, **kwargs):
        self.username = self.user.username
        super(Employee, self).save(*args, **kwargs)


class GenLink(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, null=True)
    link = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        try:
            return self.employee.user.username+'/'+str(self.link)
        except Exception:
            return f'gen_link-{self.id}'


class Task(models.Model):
    STATUS = (
        ('new', 'new'),
        ('processing', 'processing'),
        ('done', 'done')
    )
    task_giver = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, related_name='tasks_by_me', blank=True)
    assigned_to = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='tasks_to_me')
    name = models.CharField(max_length=200, null=True)
    context = models.TextField(max_length=5000)
    status = models.CharField(max_length=200, choices=STATUS, null=True)
    date_given = models.DateTimeField(auto_now_add=True, null=True)
    deadline = models.DateTimeField(null=True)
    note = models.TextField(max_length=200, null=True, blank=True)
    is_private = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Notification(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='received_messages')
    text = models.CharField(max_length=200, null=True)

    def __str__(self):
        return f"{self.text} :{self.id}"
