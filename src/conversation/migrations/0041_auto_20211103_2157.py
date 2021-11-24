# Generated by Django 3.2.9 on 2021-11-03 20:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('conversation', '0040_twitterlanguageidentifier'),
    ]

    operations = [
        migrations.AlterField(
            model_name='genericbiginttaggeditem',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='hashtag',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='treedj',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='tweetdj',
            name='deleted',
            field=models.BooleanField(default=None, help_text='Has this tweet been deleted?', null=True, verbose_name='Del'),
        ),
        migrations.AlterField(
            model_name='tweetdj',
            name='json',
            field=models.JSONField(null=True),
        ),
        migrations.AlterField(
            model_name='tweetdj',
            name='quotedstatus',
            field=models.BooleanField(default=None, help_text='Has quoted_status', null=True, verbose_name='QT'),
        ),
        migrations.AlterField(
            model_name='tweetdj',
            name='retweetedstatus',
            field=models.BooleanField(default=None, help_text='Has retweeted_status', null=True, verbose_name='RT'),
        ),
        migrations.AlterField(
            model_name='twitterlanguageidentifier',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='twitterusertimeline',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]