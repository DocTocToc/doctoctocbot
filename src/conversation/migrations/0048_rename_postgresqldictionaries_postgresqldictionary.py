# Generated by Django 3.2.12 on 2022-02-17 09:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('conversation', '0047_alter_postgresqldictionaries_options'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='PostgresqlDictionaries',
            new_name='PostgresqlDictionary',
        ),
    ]