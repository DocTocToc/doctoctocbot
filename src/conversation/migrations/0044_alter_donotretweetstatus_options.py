# Generated by Django 3.2.11 on 2022-01-22 05:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('conversation', '0043_donotretweetstatus_active'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='donotretweetstatus',
            options={'verbose_name_plural': 'statuses'},
        ),
    ]
