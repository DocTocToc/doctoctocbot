# Generated by Django 2.0.13 on 2019-04-24 05:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('moderation', '0009_category_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='quickreply',
            field=models.BooleanField(default=False, help_text='Include in DM quickreply?'),
        ),
    ]
