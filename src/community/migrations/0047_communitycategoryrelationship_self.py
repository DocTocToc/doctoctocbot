# Generated by Django 2.2.24 on 2021-09-15 18:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0046_community_twitter_self_moderation_dm'),
    ]

    operations = [
        migrations.AddField(
            model_name='communitycategoryrelationship',
            name='self',
            field=models.BooleanField(default=False, help_text='Include in self moderation?'),
        ),
    ]
