# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-10-02 02:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nominations', '0059_auto_20171002_0155'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='vet_status',
            field=models.TextField(choices=[('0', 'Pending'), ('1', 'Passed'), ('2', 'Failed')], default='0', max_length=64),
        ),
    ]