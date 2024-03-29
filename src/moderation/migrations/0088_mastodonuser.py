# Generated by Django 3.2.16 on 2022-11-18 10:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('moderation', '0087_alter_human_socialuser'),
    ]

    operations = [
        migrations.CreateModel(
            name='MastodonUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('acct', models.CharField(max_length=284, unique=True)),
                ('entity', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='moderation.entity')),
            ],
        ),
    ]
