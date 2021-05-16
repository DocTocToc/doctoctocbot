# Generated by Django 2.2.20 on 2021-05-05 12:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('moderation', '0061_socialmedia_emoji'),
        ('conversation', '0040_twitterlanguageidentifier'),
    ]

    operations = [
        migrations.CreateModel(
            name='NotificationService',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('label', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='TweetSubscription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quote_count', models.PositiveIntegerField(null=True)),
                ('retweet_count', models.PositiveIntegerField(null=True)),
                ('broadcast_count', models.PositiveIntegerField(null=True)),
                ('active', models.BooleanField(default=True)),
                ('category', models.ManyToManyField(blank=True, to='moderation.Category')),
                ('language', models.ManyToManyField(blank=True, to='conversation.TwitterLanguageIdentifier')),
                ('socialuser', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tweetsubscription', to='moderation.SocialUser')),
            ],
        ),
        migrations.CreateModel(
            name='NotificationLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('statusid', models.BigIntegerField()),
                ('success', models.BooleanField(blank=True, null=True)),
                ('log', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notificationlog', to='hive.NotificationService')),
                ('tweetsubscription', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='log', to='hive.TweetSubscription')),
            ],
        ),
    ]
