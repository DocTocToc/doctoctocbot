# Generated by Django 2.2.1 on 2019-06-08 04:32

from django.db import migrations
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_auto_20190608_0619'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogpage',
            name='intro',
            field=wagtail.core.fields.RichTextField(max_length=500),
        ),
    ]
