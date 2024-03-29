# Generated by Django 2.2.24 on 2021-10-26 03:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0053_community_pending_moderation_period'),
        ('moderation', '0067_auto_20211015_0726'),
    ]

    operations = [
        migrations.CreateModel(
            name='Prospect',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True, help_text='Is this Prospect active?')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('community', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='community.Community')),
                ('socialuser', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='moderation.SocialUser')),
            ],
        ),
    ]
