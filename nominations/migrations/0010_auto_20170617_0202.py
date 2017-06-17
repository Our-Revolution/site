# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-06-17 02:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nominations', '0009_auto_20170617_0118'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='candidate_district',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Candidate District'),
        ),
        migrations.AlterField(
            model_name='questionnaire',
            name='candidate_district',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Candidate District'),
        ),
    ]
