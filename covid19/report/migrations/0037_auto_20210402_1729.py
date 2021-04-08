# Generated by Django 3.1.5 on 2021-04-02 20:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0036_undata'),
    ]

    operations = [
        migrations.AlterField(
            model_name='undata',
            name='pct_minus_fourteen',
            field=models.FloatField(default=1),
        ),
        migrations.AlterField(
            model_name='undata',
            name='pct_plus_sixty',
            field=models.FloatField(default=1),
        ),
        migrations.AlterField(
            model_name='undata',
            name='population',
            field=models.FloatField(default=10000.0),
        ),
        migrations.AlterField(
            model_name='undata',
            name='population_female',
            field=models.FloatField(default=10000.0),
        ),
        migrations.AlterField(
            model_name='undata',
            name='population_male',
            field=models.FloatField(default=10000.0),
        ),
    ]
