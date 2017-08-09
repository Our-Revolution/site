# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-08-04 05:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nominations', '0044_auto_20170804_0548'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='status',
            field=models.CharField(choices=[('incomplete', 'Incomplete'), ('submitted', 'Submitted'), ('needs-research', 'Needs Research'), ('needs-staff-review', 'Needs Staff Review'), ('approved', 'Endorsed'), ('removed', 'Not Endorsed')], default='incomplete', max_length=64),
        ),
    ]