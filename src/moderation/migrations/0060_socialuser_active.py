# Generated by Django 2.2.13 on 2021-01-11 02:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('moderation', '0059_auto_20210106_1755'),
    ]

    operations = [
        migrations.AddField(
            model_name='socialuser',
            name='active',
            field=models.BooleanField(default=True, help_text='Is this SocialUser active? For Twitter, not active means deactivated or deleted.'),
        ),
    ]