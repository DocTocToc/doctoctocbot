# Generated by Django 2.2.24 on 2021-07-09 16:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('matrix', '0003_account'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='account',
            name='nio_store',
        ),
    ]
