# Generated by Django 3.2.16 on 2022-12-21 20:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('moderation', '0094_auto_20221219_1414'),
        ('fediverse', '0008_mastodonapp_scopes'),
    ]

    operations = [
        migrations.CreateModel(
            name='MastodonAccess',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('access_token', models.CharField(max_length=255)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('app', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='access', to='fediverse.mastodonapp')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='access', to='moderation.mastodonuser')),
            ],
        ),
    ]
