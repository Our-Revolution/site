# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-06-28 18:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nominations', '0019_auto_20170627_2306'),
    ]

    operations = [
        migrations.AlterField(
            model_name='questionnaire',
            name='status',
            field=models.CharField(blank=True, choices=[('incomplete', 'Incomplete'), ('complete', 'Complete'), ('sent', 'Sent to Candidate')], default='incomplete', max_length=16),
        ),
    ]
