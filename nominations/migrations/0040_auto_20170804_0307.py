# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-08-04 03:07
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nominations', '0039_initiativeapplication'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='application',
            options={'verbose_name': 'Candidate Application'},
        ),
        migrations.AlterModelOptions(
            name='initiativeapplication',
            options={'verbose_name': 'Ballot Initiative Applications'},
        ),
    ]
