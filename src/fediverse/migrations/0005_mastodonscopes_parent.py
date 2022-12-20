# Generated by Django 3.2.16 on 2022-12-19 19:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fediverse', '0004_mastodonscopes'),
    ]

    operations = [
        migrations.AddField(
            model_name='mastodonscopes',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='fediverse.mastodonscopes'),
        ),
    ]
