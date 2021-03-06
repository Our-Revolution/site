# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2018-02-28 21:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nominations', '0074_auto_20180228_1932'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='fundraising_date_accessed',
            field=models.DateField(blank=True, null=True, verbose_name='Date fundraising information was accessed'),
        ),
        migrations.AlterField(
            model_name='application',
            name='fundraising_date_of_filing',
            field=models.DateField(blank=True, null=True, verbose_name='Filing Date for Fundraising Report'),
        ),
        migrations.AlterField(
            model_name='application',
            name='fundraising_source_url',
            field=models.URLField(blank=True, max_length=255, null=True, verbose_name='Fundraising Source URL'),
        ),
    ]
