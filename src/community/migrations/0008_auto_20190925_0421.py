# Generated by Django 2.2.4 on 2019-09-25 02:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0007_community_crowdfunding'),
    ]

    operations = [
        migrations.AlterField(
            model_name='community',
            name='crowdfunding',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='community', to='crowdfunding.Project'),
        ),
    ]