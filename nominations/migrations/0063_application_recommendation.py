# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-10-02 03:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nominations', '0062_auto_20171002_0248'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='recommendation',
            field=models.CharField(choices=[('1', 'Endorse'), ('2', 'Do Not Endorse')], default='1', max_length=64),
        ),
    ]
