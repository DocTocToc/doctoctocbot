# Generated by Django 2.0.13 on 2019-04-03 22:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('moderation', '0005_remove_category_label_en'),
    ]

    operations = [
        migrations.RenameField(
            model_name='category',
            old_name='label_fr',
            new_name='label',
        ),
    ]