# Generated by Django 3.2.9 on 2021-11-26 06:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0057_alter_community_crowdfunding'),
    ]

    operations = [
        migrations.AddField(
            model_name='apiaccess',
            name='filter_author_self',
            field=models.BooleanField(default=False, help_text='Filter status by authenticated author.', verbose_name='Filter author self'),
        ),
    ]
