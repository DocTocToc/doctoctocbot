# Generated by Django 2.2.10 on 2020-03-18 21:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0016_retweet_allow_unknown'),
    ]

    operations = [
        migrations.AddField(
            model_name='retweet',
            name='allow_quote',
            field=models.BooleanField(default=False),
        ),
    ]
