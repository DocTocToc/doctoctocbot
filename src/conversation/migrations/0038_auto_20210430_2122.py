# Generated by Django 2.2.20 on 2021-04-30 19:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('moderation', '0061_socialmedia_emoji'),
        ('conversation', '0037_auto_20210429_2159'),
    ]

    operations = [
        migrations.AddField(
            model_name='tweetdj',
            name='quoted_by',
            field=models.ManyToManyField(blank=True, related_name='quotes', to='moderation.SocialUser'),
        ),
        migrations.AlterField(
            model_name='tweetdj',
            name='retweeted_by',
            field=models.ManyToManyField(blank=True, related_name='retweets', to='moderation.SocialUser'),
        ),
    ]
