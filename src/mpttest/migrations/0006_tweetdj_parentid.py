# Generated by Django 2.1 on 2018-09-24 08:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mpttest', '0005_auto_20180808_1912'),
    ]

    operations = [
        migrations.AddField(
            model_name='tweetdj',
            name='parentid',
            field=models.BigIntegerField(null=True),
        ),
    ]