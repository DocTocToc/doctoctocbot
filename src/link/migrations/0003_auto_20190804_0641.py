# Generated by Django 2.2.3 on 2019-08-04 04:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('link', '0002_auto_20190804_0632'),
    ]

    operations = [
        migrations.AlterField(
            model_name='website',
            name='network_location',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
