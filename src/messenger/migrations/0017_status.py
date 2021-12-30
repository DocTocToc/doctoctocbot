# Generated by Django 3.2.9 on 2021-12-26 02:32

from django.db import migrations, models
import messenger.models


class Migration(migrations.Migration):

    dependencies = [
        ('messenger', '0016_auto_20211224_0632'),
    ]

    operations = [
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('content', models.TextField(blank=True, null=True, validators=[messenger.models.validate_status])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]