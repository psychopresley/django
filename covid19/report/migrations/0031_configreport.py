# Generated by Django 3.1.5 on 2021-03-22 00:29

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0030_auto_20210321_1851'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConfigReport',
            fields=[
                ('var_name', models.CharField(default='undefined', max_length=20, primary_key=True, serialize=False)),
                ('file_path', models.FilePathField()),
                ('file_name', models.CharField(max_length=20)),
                ('date', models.DateField(default=datetime.date.today)),
                ('db_delete', models.BooleanField(default=False)),
                ('db_reload', models.BooleanField(default=False)),
                ('db_update', models.BooleanField(default=True)),
                ('confirm_delete', models.BooleanField(default=True)),
            ],
        ),
    ]
