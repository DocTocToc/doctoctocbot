# Generated by Django 3.2.9 on 2021-12-06 16:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crowdfunding', '0012_projectinvestment_campaign'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='name',
            field=models.CharField(max_length=191, unique=True),
        ),
    ]
