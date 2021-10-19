# Generated by Django 2.2.24 on 2021-10-15 05:53

from django.db import migrations


def nullify(apps, schema_editor):
    '''
    We can't import the Community model directly as it may be a newer
    version than this migration expects. We use the historical version.
    '''
    Community = apps.get_model('community', 'Community')
    for community in Community.objects.all():
        community.pending_moderation_period = None
        community.save()

class Migration(migrations.Migration):

    dependencies = [
        ('community', '0050_auto_20211015_0726'),
    ]

    operations = [
        migrations.RunPython(nullify),
    ]