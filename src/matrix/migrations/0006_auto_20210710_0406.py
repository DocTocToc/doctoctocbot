# Generated by Django 2.2.24 on 2021-07-10 02:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matrix', '0005_account_nio_store'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='access_token',
            field=models.CharField(blank=True, max_length=258),
        ),
    ]
