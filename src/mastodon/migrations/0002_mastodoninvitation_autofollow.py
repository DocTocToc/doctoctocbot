# Generated by Django 3.2.16 on 2022-11-18 11:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('moderation', '0088_mastodonuser'),
        ('mastodon', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='mastodoninvitation',
            name='autofollow',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='moderation.mastodonuser'),
        ),
    ]