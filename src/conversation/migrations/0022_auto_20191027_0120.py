# Generated by Django 2.2.4 on 2019-10-26 23:20

from django.db import migrations, models
import django.db.models.deletion
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('taggit', '0003_taggeditem_add_unique_index'),
        ('conversation', '0021_tweetdj_tags'),
    ]

    operations = [
        migrations.CreateModel(
            name='GenericBigIntTaggedItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.BigIntegerField(db_index=True, verbose_name='Object id')),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='conversation_genericbiginttaggeditem_tagged_items', to='contenttypes.ContentType', verbose_name='Content type')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='conversation_genericbiginttaggeditem_items', to='taggit.Tag')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='tweetdj',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='conversation.GenericBigIntTaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
    ]
