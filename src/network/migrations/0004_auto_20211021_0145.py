# Generated by Django 2.2.24 on 2021-10-20 23:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0003_auto_20211020_0742'),
    ]

    operations = [
        migrations.AlterField(
            model_name='network',
            name='site',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='sites.Site'),
        ),
    ]
