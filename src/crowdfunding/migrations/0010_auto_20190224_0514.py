# Generated by Django 2.0.13 on 2019-02-24 04:14

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('crowdfunding', '0009_auto_20190213_1809'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectinvestment',
            name='public',
            field=models.BooleanField(default=False),
        ),
        migrations.RemoveField(
            model_name='projectinvestment',
            name='id'
        ),
        migrations.AddField(
            model_name='projectinvestment',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, null=True, serialize=False),
        ),
    ]
