# Generated by Django 5.0.2 on 2024-06-03 22:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0020_alter_smallgroupmembership_minister'),
        ('ministry', '0012_alter_schedule_end_time_alter_schedule_start_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='smallgroupmembership',
            name='minister',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='ministry.minister'),
        ),
        migrations.DeleteModel(
            name='Ministers',
        ),
    ]
