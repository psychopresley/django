# Generated by Django 3.1.5 on 2021-04-11 19:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0052_auto_20210411_1645'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='configreport',
            name='file_path',
        ),
        migrations.AddField(
            model_name='configreport',
            name='aux_file',
            field=models.CharField(default='C:/', max_length=264),
        ),
        migrations.AddField(
            model_name='configreport',
            name='base_file',
            field=models.CharField(default='C:/', max_length=264),
        ),
    ]
