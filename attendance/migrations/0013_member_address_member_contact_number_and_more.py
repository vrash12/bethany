# Generated by Django 5.0.2 on 2024-04-17 07:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0012_alter_service_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='address',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='member',
            name='contact_number',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='member',
            name='invited_by',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='member',
            name='is_youth',
            field=models.BooleanField(default=False),
        ),
    ]