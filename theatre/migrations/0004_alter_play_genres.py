# Generated by Django 5.1.3 on 2024-11-23 10:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('theatre', '0003_alter_play_genres'),
    ]

    operations = [
        migrations.AlterField(
            model_name='play',
            name='genres',
            field=models.ManyToManyField(blank=True, to='theatre.genre'),
        ),
    ]
