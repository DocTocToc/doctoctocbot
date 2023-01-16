# Generated by Django 3.2.16 on 2022-12-19 23:41

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fediverse', '0006_alter_mastodonscopes_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='MastodonApp',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('client_name', models.CharField(max_length=255, unique=True)),
                ('api_base_url', models.URLField()),
                ('client_id', models.CharField(max_length=255, unique=True)),
                ('client_secret', models.CharField(max_length=255, unique=True)),
                ('website', models.CharField(max_length=255)),
                ('redirect_uris', django.contrib.postgres.fields.ArrayField(base_field=models.URLField(), size=None)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]