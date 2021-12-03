# Generated by Django 3.2.4 on 2021-11-21 18:34

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('hrm', '0007_auto_20211121_1817'),
    ]

    operations = [
        migrations.AlterField(
            model_name='genlink',
            name='expiration_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 11, 24, 18, 34, 24, 916597), null=True),
        ),
        migrations.AlterField(
            model_name='notification',
            name='receiver',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='received_notifications', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='notification',
            name='sender',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sent_notifications', to=settings.AUTH_USER_MODEL),
        ),
    ]
