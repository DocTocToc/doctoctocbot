# Generated by Django 2.0.10 on 2019-01-19 00:18

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crowdfunding', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='investors',
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL),
        ),
    ]