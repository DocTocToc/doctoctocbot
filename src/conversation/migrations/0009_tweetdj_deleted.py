# Generated by Django 2.0.8 on 2018-11-21 00:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('conversation', '0008_auto_20181119_1728'),
    ]

    operations = [
        migrations.AddField(
            model_name='tweetdj',
            name='deleted',
            field=models.NullBooleanField(default=None, help_text='Has this tweet been deleted?'),
        ),
    ]