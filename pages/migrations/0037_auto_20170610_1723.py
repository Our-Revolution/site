# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-06-10 17:23
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0036_auto_20170610_1722'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='peoplessummitstreampage',
            name='abstract',
        ),
        migrations.RemoveField(
            model_name='peoplessummitstreampage',
            name='body',
        ),
    ]
