# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-03-09 22:49
from __future__ import unicode_literals

from django.db import migrations
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('local_groups', '0035_auto_20170309_2236'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='country',
            field=django_countries.fields.CountryField(default='US', max_length=2, null=True),
        ),
    ]