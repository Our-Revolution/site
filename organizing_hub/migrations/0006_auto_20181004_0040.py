# -*- coding: utf-8 -*-
# Generated by Django 1.11.14 on 2018-10-04 00:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizing_hub', '0005_auto_20181003_2120'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organizinghubloginalert',
            name='alert_level',
            field=models.IntegerField(choices=[(1, 'Success (Green)'), (2, 'Info (Blue)'), (3, 'Warning (Yellow)'), (4, 'Danger (Red)')], default=3, help_text='\n        Set the alert style corresponding to Bootstrap 3 alert levels.\n\n        See: https://getbootstrap.com/docs/3.3/components/#alerts-dismissible\n        '),
        ),
    ]
