# Generated by Django 2.2.10 on 2020-03-18 15:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0009_community_helper_message'),
    ]

    operations = [
        migrations.AddField(
            model_name='retweet',
            name='moderation',
            field=models.BooleanField(default=True),
        ),
    ]
