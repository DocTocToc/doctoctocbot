# Generated by Django 3.2.16 on 2022-12-21 21:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fediverse', '0010_alter_mastodonaccess_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mastodonapp',
            name='website',
            field=models.URLField(blank=True, max_length=255, null=True),
        ),
    ]
