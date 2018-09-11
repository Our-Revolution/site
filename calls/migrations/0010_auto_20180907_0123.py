# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-09-07 01:23
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('calls', '0009_auto_20180907_0123'),
    ]

    operations = [
        migrations.AlterField(
            model_name='callcampaign',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
    ]