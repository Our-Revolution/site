# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-08-04 02:44
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nominations', '0036_remove_application_type'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Application',
            new_name='CandidateApplication',
        ),
    ]
