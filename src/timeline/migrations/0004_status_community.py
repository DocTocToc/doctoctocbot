# Generated by Django 2.2.4 on 2019-09-19 02:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0001_initial'),
        ('timeline', '0003_auto_20190224_0514'),
    ]

    operations = [
        migrations.AddField(
            model_name='status',
            name='community',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='community.Community'),
        ),
    ]
