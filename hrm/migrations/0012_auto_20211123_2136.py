# Generated by Django 3.2.4 on 2021-11-23 21:36

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hrm', '0011_auto_20211123_1949'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='rate',
            field=models.DecimalField(decimal_places=2, max_digits=2, null=True),
        ),
        migrations.AlterField(
            model_name='genlink',
            name='expiration_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 11, 26, 21, 36, 2, 829067), null=True),
        ),
    ]
