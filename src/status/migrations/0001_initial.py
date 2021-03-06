# Generated by Django 2.0.8 on 2018-11-15 02:30

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('userid', models.BigIntegerField(blank=True, null=True)),
                ('json', django.contrib.postgres.fields.jsonb.JSONField()),
                ('datetime', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'status',
                'managed': False,
            },
        ),
    ]
