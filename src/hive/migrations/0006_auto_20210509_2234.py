# Generated by Django 2.2.21 on 2021-05-09 20:34

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hive', '0005_remove_notificationlog_log'),
    ]

    operations = [
        migrations.AddField(
            model_name='notificationlog',
            name='error_log',
            field=django.contrib.postgres.fields.jsonb.JSONField(null=True),
        ),
        migrations.AddField(
            model_name='notificationlog',
            name='success_log',
            field=django.contrib.postgres.fields.jsonb.JSONField(null=True),
        ),
    ]
