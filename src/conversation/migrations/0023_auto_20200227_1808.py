# Generated by Django 2.2.10 on 2020-02-27 17:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('conversation', '0022_auto_20191027_0120'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tweetdj',
            name='deleted',
            field=models.NullBooleanField(default=None, help_text='Has this tweet been deleted?', verbose_name='Del'),
        ),
        migrations.AlterField(
            model_name='tweetdj',
            name='quotedstatus',
            field=models.NullBooleanField(default=None, help_text='Is quoted_status', verbose_name='Quote'),
        ),
        migrations.AlterField(
            model_name='tweetdj',
            name='retweetedstatus',
            field=models.NullBooleanField(default=None, help_text='Has retweeted_status', verbose_name='RT'),
        ),
    ]
