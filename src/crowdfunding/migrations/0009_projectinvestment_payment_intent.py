# Generated by Django 2.2.21 on 2021-06-13 14:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crowdfunding', '0008_campaign'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectinvestment',
            name='payment_intent',
            field=models.CharField(blank=True, max_length=27),
        ),
    ]
