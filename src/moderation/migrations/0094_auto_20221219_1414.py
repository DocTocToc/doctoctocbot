# Generated by Django 3.2.16 on 2022-12-19 13:14

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('moderation', '0093_auto_20221130_0055'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='linkedinuser',
            options={'verbose_name_plural': 'LinkedIn users'},
        ),
        migrations.CreateModel(
            name='MastodonFriend',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_list', django.contrib.postgres.fields.ArrayField(base_field=models.PositiveIntegerField(), blank=True, null=True, size=None)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='moderation.mastodonuser')),
            ],
            options={
                'get_latest_by': 'created',
            },
        ),
        migrations.CreateModel(
            name='MastodonFollower',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_list', django.contrib.postgres.fields.ArrayField(base_field=models.PositiveIntegerField(), blank=True, null=True, size=None)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='moderation.mastodonuser')),
            ],
            options={
                'get_latest_by': 'created',
            },
        ),
    ]
