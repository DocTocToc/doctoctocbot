# Generated by Django 3.2.12 on 2022-02-18 22:32

import django.contrib.postgres.search
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('conversation', '0051_alter_twitterlanguageidentifier_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='tweetdj',
            name='status_text',
            field=django.contrib.postgres.search.SearchVectorField(null=True),
        ),
    ]
