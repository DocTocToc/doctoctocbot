# Generated by Django 3.2.9 on 2021-11-03 20:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('optin', '0002_option_default_bool'),
    ]

    operations = [
        migrations.AlterField(
            model_name='option',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
