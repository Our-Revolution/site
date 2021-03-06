# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2018-01-16 21:53
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('endorsements', '0008_auto_20170118_1803'),
        ('pages', '0052_auto_20171206_0217'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidateendorsementpage',
            name='election',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='endorsements.Election'),
        ),
        migrations.AddField(
            model_name='initiativeendorsementpage',
            name='election',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='endorsements.Election'),
        ),
    ]
