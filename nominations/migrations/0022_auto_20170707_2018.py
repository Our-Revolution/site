# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-07-07 20:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nominations', '0021_auto_20170707_2012'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nomination',
            name='general_election_date',
            field=models.DateField(blank=True, null=True, verbose_name='General Election Date'),
        ),
        migrations.AlterField(
            model_name='nomination',
            name='primary_date',
            field=models.DateField(blank=True, null=True, verbose_name='Primary Election Date'),
        ),
    ]
