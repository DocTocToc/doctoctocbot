# Generated by Django 3.2.9 on 2021-11-03 20:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dm', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='directmessage',
            name='jsn',
            field=models.JSONField(),
        ),
    ]
