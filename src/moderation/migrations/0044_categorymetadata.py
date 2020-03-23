# Generated by Django 2.2.10 on 2020-03-22 23:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('moderation', '0043_auto_20200322_0219'),
    ]

    operations = [
        migrations.CreateModel(
            name='CategoryMetadata',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('label', models.CharField(max_length=255, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'Category Metadata',
                'ordering': ('name',),
            },
        ),
    ]