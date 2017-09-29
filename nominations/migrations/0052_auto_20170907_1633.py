# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-09-07 16:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nominations', '0051_questionnaire_completed_by_candidate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='status',
            field=models.CharField(choices=[('incomplete', 'Incomplete'), ('submitted', 'Submitted'), ('needs-research', 'Needs Research'), ('needs-staff-review', 'Needs Staff Review'), ('approved', 'Endorsed'), ('removed', 'Not Endorsed'), ('expired', 'Expired'), ('no-action', 'No Action Needed Now')], default='incomplete', max_length=64),
        ),
    ]