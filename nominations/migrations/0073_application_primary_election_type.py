# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2018-02-27 20:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nominations', '0072_auto_20180227_0103'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='primary_election_type',
            field=models.IntegerField(blank=True, choices=[(1, 'Closed Primary'), (2, 'Partially Closed Primary'), (3, 'Partially Open Primary'), (4, 'Open to Unaffiliated Voters Primary'), (5, 'Open Primary'), (6, 'Top-Two Primary'), (7, 'Presidential Primary'), (99, 'Other')], null=True),
        ),
    ]
