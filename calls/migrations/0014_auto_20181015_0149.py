# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-10-15 01:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calls', '0013_auto_20181001_2256'),
    ]

    operations = [
        migrations.AlterField(
            model_name='callresponse',
            name='answer',
            field=models.IntegerField(blank=True, choices=[(1, 'Yes'), (2, 'No'), (3, 'Maybe'), (4, 'No answer'), (5, 'Wrong number'), (6, 'Busy'), (7, 'Not Home'), (8, 'Do not call')], null=True),
        ),
    ]
