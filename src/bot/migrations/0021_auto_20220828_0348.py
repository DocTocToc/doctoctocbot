# Generated by Django 3.2.15 on 2022-08-28 01:48

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0020_accesstoken'),
    ]

    operations = [
        migrations.AddField(
            model_name='accesstoken',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='accesstoken',
            name='updated',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
