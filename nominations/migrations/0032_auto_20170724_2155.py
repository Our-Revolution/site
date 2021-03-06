# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-07-24 21:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nominations', '0031_auto_20170715_1506'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='submitted_dt',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='response',
            name='response',
            field=models.CharField(choices=[('a', 'Strongly Agree'), ('b', 'Strongly Disagree'), ('c', 'Somewhat Agree'), ('d', 'Somewhat Disagree')], max_length=1),
        ),
    ]
