# Generated by Django 3.2.4 on 2021-11-22 22:02

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hrm', '0009_auto_20211122_2201'),
    ]

    operations = [
        migrations.AlterField(
            model_name='genlink',
            name='expiration_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 11, 25, 22, 2, 21, 145354), null=True),
        ),
        migrations.AlterField(
            model_name='task',
            name='status',
            field=models.CharField(blank=True, choices=[('new', 'new'), ('processing', 'processing'), ('done', 'done')], default='new', max_length=200, null=True),
        ),
    ]
