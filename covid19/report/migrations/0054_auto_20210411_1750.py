# Generated by Django 3.1.5 on 2021-04-11 20:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0053_auto_20210411_1650'),
    ]

    operations = [
        migrations.AlterField(
            model_name='configreport',
            name='aux_file',
            field=models.FilePathField(path='C:\\Users\\user\\Documents\\GitHub\\COVID-19\\consolidated_data'),
        ),
        migrations.AlterField(
            model_name='configreport',
            name='base_file',
            field=models.FilePathField(path='C:\\Users\\user\\Documents\\GitHub\\COVID-19\\consolidated_data'),
        ),
    ]
