# Generated by Django 2.0.13 on 2019-05-07 08:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('moderation', '0012_category_socialgraph'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='color',
            field=models.CharField(blank=True, max_length=20, null=True, unique=True),
        ),
    ]
