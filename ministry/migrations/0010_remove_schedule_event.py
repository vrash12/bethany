# Generated by Django 5.0.2 on 2024-05-26 03:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ministry', '0009_remove_schedule_end_time_remove_schedule_start_time_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='schedule',
            name='event',
        ),
    ]