# Generated by Django 3.2.15 on 2022-08-26 14:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0018_twitterapi_twitterapp_twitterscopes'),
    ]

    operations = [
        migrations.AddField(
            model_name='twitterapp',
            name='api',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='bot.twitterapi'),
        ),
        migrations.AddField(
            model_name='twitterapp',
            name='scopes',
            field=models.ManyToManyField(to='bot.TwitterScopes'),
        ),
    ]