# Generated by Django 3.1.5 on 2021-02-10 16:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='countryinfo',
            name='id',
        ),
        migrations.AlterField(
            model_name='countryinfo',
            name='country',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='report.country'),
        ),
        migrations.AlterField(
            model_name='countryinfo',
            name='latitude',
            field=models.FloatField(default=90),
        ),
        migrations.AlterField(
            model_name='countryinfo',
            name='longitude',
            field=models.FloatField(default=0),
        ),
    ]
