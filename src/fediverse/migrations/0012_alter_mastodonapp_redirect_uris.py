# Generated by Django 3.2.16 on 2022-12-21 21:58

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fediverse', '0011_alter_mastodonapp_website'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mastodonapp',
            name='redirect_uris',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.URLField(), blank=True, null=True, size=None),
        ),
    ]
