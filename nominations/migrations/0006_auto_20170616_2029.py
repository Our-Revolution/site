# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-06-16 20:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nominations', '0005_auto_20170616_2002'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nomination',
            name='group_nomination_process',
            field=models.TextField(max_length=500, null=True, verbose_name="Briefly describe your group's nomination process"),
        ),
    ]
