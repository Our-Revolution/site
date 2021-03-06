# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-08-04 03:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nominations', '0040_auto_20170804_0307'),
    ]

    operations = [
        migrations.AddField(
            model_name='initiativeapplication',
            name='city',
            field=models.CharField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='initiativeapplication',
            name='donate_url',
            field=models.URLField(blank=True, max_length=255, null=True, verbose_name='Donate URL'),
        ),
        migrations.AddField(
            model_name='initiativeapplication',
            name='election_date',
            field=models.DateField(null=True, verbose_name='Election Date'),
        ),
        migrations.AddField(
            model_name='initiativeapplication',
            name='volunteer_url',
            field=models.URLField(blank=True, max_length=255, null=True, verbose_name='Volunteer URL'),
        ),
        migrations.AddField(
            model_name='initiativeapplication',
            name='website_url',
            field=models.URLField(max_length=255, null=True, verbose_name='Initiative Website URL'),
        ),
        migrations.AlterField(
            model_name='initiativeapplication',
            name='name',
            field=models.CharField(max_length=254, null=True),
        ),
    ]
