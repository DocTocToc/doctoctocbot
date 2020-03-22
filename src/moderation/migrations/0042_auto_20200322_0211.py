# Generated by Django 2.2.10 on 2020-03-22 01:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('moderation', '0041_auto_20200321_0210'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='field',
            field=models.ForeignKey(blank=True, help_text='Field as a MeSH heading', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='category_field', to='mesh.Mesh'),
        ),
        migrations.AlterField(
            model_name='category',
            name='mesh',
            field=models.ForeignKey(blank=True, help_text='Category as a MeSH heading', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='category', to='mesh.Mesh'),
        ),
    ]
