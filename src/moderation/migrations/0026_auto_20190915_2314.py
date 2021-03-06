# Generated by Django 2.2.4 on 2019-09-15 21:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0001_initial'),
        ('moderation', '0025_usercategoryrelationship_community'),
    ]

    operations = [
        migrations.AddField(
            model_name='twitterlist',
            name='community',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='community.Community'),
        ),
        migrations.AlterUniqueTogether(
            name='usercategoryrelationship',
            unique_together={('social_user', 'category', 'community')},
        ),
    ]
