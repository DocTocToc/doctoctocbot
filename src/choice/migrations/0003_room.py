# Generated by Django 2.2.24 on 2021-06-29 04:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('choice', '0002_diploma_discipline'),
    ]

    operations = [
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('room_id', models.CharField(blank=True, max_length=255)),
                ('room_alias', models.CharField(blank=True, max_length=255)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('diploma', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='diploma', to='choice.Diploma')),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='room', to='choice.School')),
            ],
            options={
                'ordering': ('school__tag', 'diploma__label'),
                'unique_together': {('school', 'diploma')},
            },
        ),
    ]