# Generated by Django 5.0.2 on 2024-03-29 21:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0008_alter_attendance_service'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendance',
            name='service',
            field=models.ForeignKey(default=7, on_delete=django.db.models.deletion.CASCADE, to='attendance.service'),
        ),
    ]
