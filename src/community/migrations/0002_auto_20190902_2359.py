# Generated by Django 2.2.4 on 2019-09-02 21:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='retweet',
            name='reweet',
        ),
        migrations.AddField(
            model_name='retweet',
            name='retweet',
            field=models.BooleanField(default=False),
        ),
    ]