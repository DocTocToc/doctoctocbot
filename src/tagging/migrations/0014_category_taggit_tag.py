# Generated by Django 2.2.13 on 2020-08-28 05:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0003_taggeditem_add_unique_index'),
        ('tagging', '0013_category_taggit'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='taggit_tag',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='tagging_category', to='taggit.Tag'),
        ),
    ]
