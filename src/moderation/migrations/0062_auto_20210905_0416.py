# Generated by Django 2.2.24 on 2021-09-05 02:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('moderation', '0061_socialmedia_emoji'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='queue',
            options={'ordering': ('-version_start_date',)},
        ),
        migrations.AlterUniqueTogether(
            name='queue',
            unique_together=set(),
        ),
    ]
