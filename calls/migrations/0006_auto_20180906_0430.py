# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-09-06 04:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calls', '0005_auto_20180808_2301'),
    ]

    operations = [
        migrations.AlterField(
            model_name='callcampaign',
            name='postal_code',
            field=models.CharField(max_length=12, verbose_name='Zip Code'),
        ),
    ]
