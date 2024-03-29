# Generated by Django 3.2.9 on 2021-12-20 05:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('crowdfunding', '0020_alter_projectinvestment_invoice'),
        ('messenger', '0013_auto_20211103_2157'),
    ]

    operations = [
        migrations.CreateModel(
            name='MessengerCrowdfunding',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('toggle', models.BooleanField(help_text='When set to True, message will be sent to users who participated to this crowdfunding campaign. When set to False, message will not be sent to users who participated to this crowdfunding campaign.', null=True)),
                ('crowdfunding_campaign', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='crowdfunding.campaign')),
                ('messenger_campaign', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='messenger.campaign')),
            ],
        ),
        migrations.AddField(
            model_name='campaign',
            name='crowdfunding',
            field=models.ManyToManyField(related_name='messenger_campaigns', through='messenger.MessengerCrowdfunding', to='crowdfunding.Campaign'),
        ),
    ]
