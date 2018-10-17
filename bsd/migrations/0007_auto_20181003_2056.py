# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-10-03 20:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bsd', '0006_auto_20180927_2359'),
    ]

    operations = [
        migrations.AddField(
            model_name='geotarget',
            name='primary_addresses_only',
            field=models.BooleanField(default=True, help_text='Recommended'),
        ),
        migrations.AlterField(
            model_name='geotarget',
            name='geo_json',
            field=models.TextField(help_text='Get this from census.gov or web search, or ask Organizing'),
        ),
    ]