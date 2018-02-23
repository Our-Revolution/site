# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2018-02-07 19:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('local_groups', '0060_auto_20171213_2208'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='group_type',
            field=models.IntegerField(choices=[(1, 'State Organizing Committee'), (2, 'State Chapter'), (3, 'Campus'), (4, 'Local Group')], default=4),
        ),
    ]