# Generated by Django 2.2.9 on 2019-12-30 19:23

import community.models
from django.db import migrations, models
import django.db.models.deletion
import moderation.models
import versions.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('community', '0007_auto_20191022_0037'),
        ('moderation', '0037_auto_20191101_0133'),
    ]

    operations = [
        migrations.CreateModel(
            name='Queue',
            fields=[
                ('id', models.UUIDField(primary_key=True, serialize=False)),
                ('identity', models.UUIDField()),
                ('version_start_date', models.DateTimeField()),
                ('version_end_date', models.DateTimeField(blank=True, default=None, null=True)),
                ('version_birth_date', models.DateTimeField()),
                ('uid', models.BigIntegerField()),
                ('state', models.CharField(choices=[('accept', 'Accepted'), ('decline', 'Declined'), ('cancel', 'Canceled'), ('pending', 'Pending')], default='pending', max_length=7)),
                ('community', models.ForeignKey(default=community.models.get_default_community, on_delete=django.db.models.deletion.CASCADE, related_name='request_queue', to='community.Community')),
                ('socialmedia', models.ForeignKey(default=moderation.models.get_default_socialmedia, on_delete=django.db.models.deletion.CASCADE, related_name='request_queue', to='moderation.SocialMedia')),
            ],
        ),
        migrations.CreateModel(
            name='Process',
            fields=[
                ('id', models.UUIDField(primary_key=True, serialize=False)),
                ('identity', models.UUIDField()),
                ('version_start_date', models.DateTimeField()),
                ('version_end_date', models.DateTimeField(blank=True, default=None, null=True)),
                ('version_birth_date', models.DateTimeField()),
                ('processor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='request_process', to='moderation.SocialUser')),
                ('queue', versions.fields.VersionedForeignKey(on_delete=django.db.models.deletion.CASCADE, to='request.Queue')),
            ],
            options={
                'verbose_name_plural': 'processes',
                'unique_together': {('queue', 'processor')},
            },
        ),
    ]
