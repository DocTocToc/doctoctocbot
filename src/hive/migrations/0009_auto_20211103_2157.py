# Generated by Django 3.2.9 on 2021-11-03 20:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hive', '0008_auto_20210920_0910'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notificationlog',
            name='error_log',
            field=models.JSONField(null=True),
        ),
        migrations.AlterField(
            model_name='notificationlog',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='notificationlog',
            name='success_log',
            field=models.JSONField(null=True),
        ),
        migrations.AlterField(
            model_name='notificationservice',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='tweetsubscription',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
