# Generated by Django 3.1.5 on 2021-04-11 18:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0049_auto_20210411_1509'),
    ]

    operations = [
        migrations.AlterField(
            model_name='configreport',
            name='var_name',
            field=models.CharField(default='undefined', max_length=30, primary_key=True, serialize=False),
        ),
    ]
