# Generated by Django 3.2.11 on 2022-01-25 23:58

from decimal import Decimal
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('moderation', '0078_filter_profile_update'),
    ]

    operations = [
        migrations.AddField(
            model_name='filter',
            name='member_follower_ratio',
            field=models.DecimalField(decimal_places=2, default=Decimal('0'), help_text='Minimum member followers / total followers ratio required', max_digits=3, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)]),
        ),
    ]
