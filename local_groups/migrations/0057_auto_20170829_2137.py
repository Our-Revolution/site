# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-08-29 21:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('local_groups', '0056_auto_20170829_1818'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='mou_url',
            field=models.URLField(blank=True, max_length=255, null=True, verbose_name='MOU URL'),
        ),
    ]
