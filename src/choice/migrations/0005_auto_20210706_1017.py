# Generated by Django 2.2.24 on 2021-07-06 08:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('choice', '0004_auto_20210705_0640'),
    ]

    operations = [
        migrations.AddField(
            model_name='diploma',
            name='slug',
            field=models.SlugField(null=True),
        ),
        migrations.AddField(
            model_name='discipline',
            name='slug',
            field=models.SlugField(null=True),
        ),
        migrations.AddField(
            model_name='participanttype',
            name='slug',
            field=models.SlugField(null=True),
        ),
        migrations.AddField(
            model_name='school',
            name='slug',
            field=models.SlugField(null=True),
        ),
    ]
