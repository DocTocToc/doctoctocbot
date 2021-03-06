# Generated by Django 2.2.10 on 2020-02-12 03:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('invitations', '0003_auto_20151126_1523'),
        ('moderation', '0037_auto_20191101_0133'),
    ]

    operations = [
        migrations.CreateModel(
            name='CategoryInvitation',
            fields=[
                ('invitation_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='invitations.Invitation')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='moderation.Category')),
            ],
            options={
                'abstract': False,
            },
            bases=('invitations.invitation',),
        ),
    ]
