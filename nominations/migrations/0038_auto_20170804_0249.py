# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-08-04 02:49
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nominations', '0037_auto_20170804_0244'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='CandidateApplication',
            new_name='Application',
        ),
    ]
