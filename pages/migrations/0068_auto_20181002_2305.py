# -*- coding: utf-8 -*-
# Generated by Django 1.11.14 on 2018-10-02 23:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0067_auto_20181002_2302'),
    ]

    operations = [
        migrations.AlterField(
            model_name='candidateendorsementindexpage',
            name='button_show',
            field=models.BooleanField(default=False, help_text='Show nominations platform Get Started button.'),
        ),
    ]