# Generated by Django 2.2.1 on 2019-06-03 01:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('conversation', '0012_auto_20190603_0213'),
    ]

    operations = [
        migrations.AlterField(
            model_name='treedj',
            name='level',
            field=models.PositiveIntegerField(db_index=True, editable=False),
        ),
        migrations.AlterField(
            model_name='treedj',
            name='lft',
            field=models.PositiveIntegerField(db_index=True, editable=False),
        ),
        migrations.AlterField(
            model_name='treedj',
            name='rght',
            field=models.PositiveIntegerField(db_index=True, editable=False),
        ),
    ]
