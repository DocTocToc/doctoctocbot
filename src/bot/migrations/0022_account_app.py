# Generated by Django 3.2.15 on 2022-08-31 23:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0021_auto_20220828_0348'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='app',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='bot.twitterapp'),
        ),
    ]
