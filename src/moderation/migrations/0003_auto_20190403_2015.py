# Generated by Django 2.0.13 on 2019-04-03 18:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('moderation', '0002_twitterlist'),
    ]

    operations = [
        migrations.RenameField(
            model_name='twitterlist',
            old_name='description',
            new_name='twitter_description',
        ),
    ]
