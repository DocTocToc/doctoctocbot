# Generated by Django 3.2.16 on 2022-12-24 00:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('moderation', '0096_alter_mastodonfriend_id_list'),
        ('conversation', '0057_tweetdj_conversatio_created_a2bbc2_idx'),
        ('community', '0071_community_mastodon_access'),
    ]

    operations = [
        migrations.CreateModel(
            name='Reblog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reblog', models.BooleanField(default=False)),
                ('favourite', models.BooleanField(default=False)),
                ('bookmark', models.BooleanField(default=False)),
                ('moderation', models.BooleanField(default=True)),
                ('require_question', models.BooleanField(default=True)),
                ('allow_reblogged', models.BooleanField(default=False)),
                ('require_follower', models.BooleanField(default=True)),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='moderation.category')),
                ('community', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='community.community')),
                ('hashtag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='conversation.hashtag')),
            ],
            options={
                'unique_together': {('community', 'hashtag', 'category')},
            },
        ),
    ]