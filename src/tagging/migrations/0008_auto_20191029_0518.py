# Generated by Django 2.2.4 on 2019-10-29 04:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tagging', '0007_auto_20191029_0434'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ['order', 'tag'], 'verbose_name_plural': 'categories'},
        ),
        migrations.AddField(
            model_name='category',
            name='hashtag',
            field=models.BooleanField(default=False),
        ),
    ]
