# Generated by Django 3.2.20 on 2023-08-23 13:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('moderation', '0097_alter_mastodonfollower_id_list'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mastodonuser',
            name='local_id',
            field=models.BigIntegerField(null=True, unique=True),
        ),
    ]