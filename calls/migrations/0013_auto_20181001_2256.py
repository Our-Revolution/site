# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-10-01 22:56
from __future__ import unicode_literals

from django.db import migrations
import localflavor.us.models


class Migration(migrations.Migration):

    dependencies = [
        ('calls', '0012_auto_20180929_0208'),
    ]

    operations = [
        migrations.AlterField(
            model_name='callcampaign',
            name='state_or_territory',
            field=localflavor.us.models.USStateField(max_length=2, verbose_name='State or Territory'),
        ),
    ]
