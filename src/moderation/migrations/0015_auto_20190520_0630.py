# Generated by Django 2.0.13 on 2019-05-20 04:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('moderation', '0014_moderator'),
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('img', models.ImageField(blank=True, null=True, upload_to='moderation/')),
            ],
        ),
    ]
