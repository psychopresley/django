# Generated by Django 3.1.5 on 2021-03-01 18:00

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('report', '0015_auto_20210301_1500'),
    ]

    operations = [
        migrations.CreateModel(
            name='Country',
            fields=[
                ('name', models.CharField(default='undefined', max_length=60, primary_key=True, serialize=False)),
                ('latitude', models.FloatField(default=90)),
                ('longitude', models.FloatField(default=0)),
                ('region', models.CharField(max_length=30)),
                ('internet_code', models.CharField(default='br', max_length=2)),
                ('map_image', models.URLField(default='www.google.com', max_length=264)),
            ],
        ),
    ]
