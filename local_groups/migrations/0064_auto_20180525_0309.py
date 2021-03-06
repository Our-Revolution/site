# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2018-05-25 03:09
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('local_groups', '0063_event'),
    ]

    operations = [
        migrations.CreateModel(
            name='LocalGroupAffiliation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('auth_groups', models.ManyToManyField(to='auth.Group')),
                ('local_group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='local_groups.Group')),
            ],
        ),
        migrations.CreateModel(
            name='LocalGroupProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='localgroupaffiliation',
            name='local_group_profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='local_groups.LocalGroupProfile'),
        ),
        migrations.AlterUniqueTogether(
            name='localgroupaffiliation',
            unique_together=set([('local_group', 'local_group_profile')]),
        ),
    ]
