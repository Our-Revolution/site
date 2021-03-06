# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-08-07 17:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('local_groups', '0051_auto_20170807_1750'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='status',
            field=models.CharField(choices=[('submitted', 'Submitted'), ('signed-mou', 'Signed MOU'), ('signed-mou-new', 'Signed New MOU'), ('inactive-unsigned', 'Inactive Unsigned'), ('approved', 'Approved'), ('removed', 'Removed')], default='submitted', max_length=64),
        ),
    ]
