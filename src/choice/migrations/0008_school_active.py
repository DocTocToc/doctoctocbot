# Generated by Django 2.2.24 on 2021-07-17 15:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('choice', '0007_auto_20210711_0958'),
    ]

    operations = [
        migrations.AddField(
            model_name='school',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]