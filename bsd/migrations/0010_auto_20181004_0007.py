# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-10-04 00:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bsd', '0009_auto_20181003_2131'),
    ]

    operations = [
        migrations.AlterField(
            model_name='geotarget',
            name='status',
            field=models.IntegerField(choices=[(1, 'New'), (10, 'In Queue'), (20, 'Build In Progress'), (30, 'Complete'), (40, 'No Results')], default=1),
        ),
    ]
