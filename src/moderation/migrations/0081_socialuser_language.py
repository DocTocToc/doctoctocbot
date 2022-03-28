# Generated by Django 3.2.12 on 2022-02-17 14:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('conversation', '0049_twitterlanguageidentifier_postgresql_dictionary'),
        ('moderation', '0080_alter_socialuser_user_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='socialuser',
            name='language',
            field=models.ForeignKey(blank=True, help_text='default language as a TwitterLanguageIdentifier object', null=True, on_delete=django.db.models.deletion.PROTECT, to='conversation.twitterlanguageidentifier'),
        ),
    ]