# Generated by Django 3.2.15 on 2022-09-02 21:13

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messenger', '0026_alter_campaign_crowdfunding_project'),
    ]

    operations = [
        migrations.AddField(
            model_name='receipt',
            name='error_codes',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.PositiveIntegerField(), blank=True, null=True, size=None),
        ),
    ]