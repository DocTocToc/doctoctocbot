# Generated by Django 3.2.16 on 2022-10-29 06:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0068_alter_community_site'),
    ]

    operations = [
        migrations.AddField(
            model_name='communitycategoryrelationship',
            name='follower_chart',
            field=models.BooleanField(default=False, help_text='Add this category to the follower chart'),
        ),
    ]