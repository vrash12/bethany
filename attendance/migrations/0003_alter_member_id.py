# Generated by Django 5.0.2 on 2024-03-22 00:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0002_attendance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]