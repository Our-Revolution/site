# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-04-21 21:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('local_groups', '0047_auto_20170329_2254'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='state_organizing_committee',
            field=models.BooleanField(default=False),
        ),
    ]
