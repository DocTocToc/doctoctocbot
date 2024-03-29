# Generated by Django 2.2.24 on 2021-08-02 19:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('moderation', '0061_socialmedia_emoji'),
        ('hcp', '0003_auto_20210730_1516'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaxonomyCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(blank=True, max_length=10, null=True, unique=True)),
                ('grouping', models.CharField(max_length=255)),
                ('classification', models.CharField(max_length=255)),
                ('specialization', models.CharField(max_length=255)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='moderation.Category')),
            ],
        ),
    ]
