# Generated by Django 2.0.8 on 2018-11-15 02:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('conversation', '0006_auto_20181111_0126'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tweetdj',
            name='like',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='tweetdj',
            name='reply',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='tweetdj',
            name='retweet',
            field=models.PositiveIntegerField(null=True),
        ),
    ]