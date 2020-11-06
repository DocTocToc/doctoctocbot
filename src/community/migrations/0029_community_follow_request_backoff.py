# Generated by Django 2.2.13 on 2020-07-03 03:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0028_text_textdescription'),
    ]

    operations = [
        migrations.AddField(
            model_name='community',
            name='follow_request_backoff',
            field=models.PositiveIntegerField(default=1, help_text='Period in hour during which a follow request will be automatically declined if the previous one was declined.'),
        ),
    ]