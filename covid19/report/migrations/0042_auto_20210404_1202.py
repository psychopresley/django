# Generated by Django 3.1.5 on 2021-04-04 15:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0041_auto_20210403_1308'),
    ]

    operations = [
        migrations.AlterField(
            model_name='isocodedata',
            name='country_name',
            field=models.CharField(default='undefined', max_length=60),
        ),
        migrations.AlterField(
            model_name='isocodedata',
            name='iso_code',
            field=models.CharField(default='00', max_length=2, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='isocodedata',
            name='un_name',
            field=models.CharField(default='undefined', max_length=60),
        ),
    ]
