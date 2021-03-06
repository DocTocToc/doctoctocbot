# Generated by Django 2.2.13 on 2020-07-04 13:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0029_community_follow_request_backoff'),
    ]

    operations = [
        migrations.AddField(
            model_name='community',
            name='request_queue_backoff',
            field=models.PositiveIntegerField(default=30, help_text='For a given user, wait this amount of time after one of its  queues was modified before a new queue can be created.'),
        ),
    ]
