# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-07-13 16:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nominations', '0029_application_vol_incumbent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='questionnaire',
            name='general_election_date',
            field=models.DateField(default='1941-09-08', verbose_name='General Election Date'),
            preserve_default=False,
        ),
    ]
