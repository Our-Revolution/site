# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2018-01-31 22:12
from __future__ import unicode_literals

from django.db import migrations
import localflavor.us.models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0055_auto_20180130_2150'),
    ]

    operations = [
        migrations.AlterField(
            model_name='candidateendorsementpage',
            name='state_or_territory',
            field=localflavor.us.models.USStateField(blank=True, max_length=2, null=True),
        ),
    ]