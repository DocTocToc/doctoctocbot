# Generated by Django 3.2.16 on 2022-12-19 19:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fediverse', '0003_alter_mastodoninvitation_socialuser'),
    ]

    operations = [
        migrations.CreateModel(
            name='MastodonScopes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('scope', models.CharField(max_length=255, unique=True)),
                ('description', models.CharField(blank=True, max_length=255)),
            ],
        ),
    ]
