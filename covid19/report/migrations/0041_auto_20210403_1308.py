# Generated by Django 3.1.5 on 2021-04-03 16:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0040_auto_20210403_1255'),
    ]

    operations = [
        migrations.AlterField(
            model_name='isocodedata',
            name='country_name',
            field=models.CharField(default=models.CharField(default='undefined', max_length=60), max_length=60),
        ),
        migrations.AlterField(
            model_name='isocodedata',
            name='un_name',
            field=models.CharField(default=models.CharField(default='undefined', max_length=60), max_length=60),
        ),
    ]
