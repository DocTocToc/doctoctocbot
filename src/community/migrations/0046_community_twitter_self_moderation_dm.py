# Generated by Django 2.2.24 on 2021-09-11 02:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0045_community_moderator_moderation_period'),
    ]

    operations = [
        migrations.AddField(
            model_name='community',
            name='twitter_self_moderation_dm',
            field=models.TextField(blank=True, null=True),
        ),
    ]