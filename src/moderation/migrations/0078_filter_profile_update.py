# Generated by Django 3.2.11 on 2022-01-14 20:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('moderation', '0077_filter_account_age'),
    ]

    operations = [
        migrations.AddField(
            model_name='filter',
            name='profile_update',
            field=models.DurationField(blank=True, help_text='Duration after which user profile should be updated', null=True),
        ),
    ]
