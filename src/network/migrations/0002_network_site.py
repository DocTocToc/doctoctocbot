# Generated by Django 2.2.24 on 2021-10-20 05:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0002_auto_20190128_0414'),
        ('network', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='network',
            name='site',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='sites.Site'),
        ),
    ]
