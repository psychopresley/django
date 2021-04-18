# Generated by Django 3.1.5 on 2021-04-12 09:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0061_delete_configreport'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConfigReport',
            fields=[
                ('var_name', models.CharField(default='dbconfig_', max_length=30, primary_key=True, serialize=False)),
                ('base_file', models.FilePathField(path='C:\\Users\\user\\Documents\\GitHub\\COVID-19\\consolidated_data')),
                ('aux_file_one', models.FilePathField(path='C:\\Users\\user\\Documents\\GitHub\\django\\covid19\\static\\report\\config')),
                ('aux_file_two', models.FilePathField(path='C:\\Users\\user\\Documents\\GitHub\\django\\covid19\\static\\report\\config')),
                ('date', models.CharField(default='not specified', max_length=60)),
                ('task', models.IntegerField(choices=[(0, 'delete'), (1, 'update'), (2, 'reload')], default=1)),
                ('confirm_delete', models.BooleanField(default=True)),
                ('auto_exec', models.BooleanField(default=True)),
                ('time_exec', models.FloatField(default=1.0)),
                ('log_status', models.IntegerField(choices=[(0, 'No changes detected'), (1, 'Success - database updated'), (2, 'Failure - something went wrong.')], default=1)),
            ],
        ),
    ]
