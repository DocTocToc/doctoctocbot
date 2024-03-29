# Generated by Django 2.2.24 on 2021-09-05 04:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0044_auto_20210415_0403'),
    ]

    operations = [
        migrations.AddField(
            model_name='community',
            name='moderator_moderation_period',
            field=models.DurationField(blank=True, help_text='Interval before same moderation sent again to moderator', null=True),
        ),
    ]
