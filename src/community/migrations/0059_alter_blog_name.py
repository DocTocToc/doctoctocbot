# Generated by Django 3.2.9 on 2021-12-06 16:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0058_apiaccess_filter_author_self'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blog',
            name='name',
            field=models.CharField(help_text='Name of the blog.', max_length=254, unique=True),
        ),
    ]