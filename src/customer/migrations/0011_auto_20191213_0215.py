# Generated by Django 2.2.4 on 2019-12-13 01:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0010_product_copper_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='product_code',
            field=models.CharField(blank=True, max_length=255, null=True, unique=True),
        ),
    ]
