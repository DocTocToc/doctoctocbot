# Generated by Django 2.0.13 on 2019-02-25 05:21

from decimal import Decimal
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('crowdfunding', '0012_auto_20190224_0523'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tiers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag', models.CharField(max_length=191)),
                ('description', models.CharField(max_length=191)),
                ('emoji', models.CharField(blank=True, max_length=4)),
                ('image', models.ImageField(blank=True, upload_to='')),
                ('min', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=12)),
                ('max', models.DecimalField(decimal_places=2, default=Decimal('Infinity'), max_digits=12)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crowdfunding.Project')),
            ],
        ),
    ]
