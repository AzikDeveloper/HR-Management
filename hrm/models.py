from django.db import models
from django.contrib.auth.models import User
import uuid
from datetime import datetime, timedelta


class Section(models.Model):
    name = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.name


class Address(models.Model):
    home_number = models.IntegerField(null=True)
    street = models.CharField(max_length=200, null=True)
    state = models.CharField(max_length=200, null=True)
    city = models.CharField(max_length=200, null=True)
    zip_code = models.IntegerField(null=True)
    country = models.CharField(max_length=200, null=True)

    def __str__(self):
        return f"address({self.id})"


class Info(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    photo = models.ImageField(upload_to='images/', null=True, blank=True)
    salary = models.CharField(max_length=200, null=True, blank=True)
    phone = models.CharField(max_length=200, null=True, blank=True)
    about = models.TextField(max_length=500, null=True, blank=True)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, related_name='employees_by_address', null=True,
                                blank=True)
    section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='employees_by_section')

    def __str__(self):
        return self.user.username


class GenLink(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    expiration_date = models.DateTimeField(null=True, default=datetime.today() + timedelta(days=3))
    used = models.BooleanField(default=False)

    def is_expired(self):
        today = datetime.today()
        if self.expiration_date:
            if self.expiration_date >= today:
                return False
            else:
                return True
        else:
            return True

    def __str__(self):
        try:
            return f"{self.user.username}/{self.id}/{'used' if self.used else 'not used'}/{'expired' if self.is_expired() else ''}"
        except Exception:
            return f"gen-link/{self.id}/{'used' if self.used else 'not used'}/{'expired' if self.is_expired() else ''}"


class Task(models.Model):
    STATUS = (
        ('new', 'new'),
        ('processing', 'processing'),
        ('done', 'done')
    )
    task_giver = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='tasks_by_me',
                                   blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='tasks_to_me')
    name = models.CharField(max_length=200, null=True)
    context = models.TextField(max_length=5000)
    status = models.CharField(max_length=200, choices=STATUS, null=True, blank=True, default='new')
    date_given = models.DateTimeField(auto_now_add=True, null=True)
    deadline = models.DateTimeField(null=True)
    note = models.TextField(max_length=200, null=True, blank=True)
    rate = models.FloatField(null=True, blank=True)
    is_private = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Notification(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='sent_notifications')
    receiver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='received_notifications')
    text = models.CharField(max_length=200, null=True)

    def __str__(self):
        return f"{self.text} :{self.id}"
