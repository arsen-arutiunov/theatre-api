# Generated by Django 5.1.3 on 2024-11-23 10:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('theatre', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='play',
            name='genres',
            field=models.ManyToManyField(to='theatre.genre'),
        ),
    ]
