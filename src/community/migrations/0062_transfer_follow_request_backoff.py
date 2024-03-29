# Generated by Django 3.2.9 on 2021-12-14 23:58
from datetime import timedelta
from django.db import migrations


def forwards_func(apps, schema_editor):
    Community = apps.get_model('community', 'Community')
    for community in Community.objects.all():
        hours: int = community.follow_request_backoff
        if not hours:
            continue
        backoff = timedelta(hours=hours)
        community.follow_request_backoff_new = backoff
        community.save()

def reverse_func(apps, schema_editor):
    Community = apps.get_model('community', 'Community')
    for community in Community.objects.all():
        duration: timedelta = community.follow_request_backoff_new
        if not duration:
            continue
        totsec = duration.total_seconds()
        hours = totsec//3600
        community.follow_request_backoff = hours
        community.save()

class Migration(migrations.Migration):

    dependencies = [
        ('community', '0061_community_follow_request_backoff_new'),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ]
