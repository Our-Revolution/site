# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-09-28 15:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nominations', '0054_auto_20170928_1551'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='vol_notes',
            field=models.TextField(blank=True, help_text='Max length 1000 characters.', max_length=1000, null=True, verbose_name='Notes:'),
        ),
    ]