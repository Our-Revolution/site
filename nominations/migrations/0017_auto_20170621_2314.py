# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-06-21 23:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nominations', '0016_questionnaire_candidate_volunteer_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='response',
            name='position',
            field=models.TextField(blank=True, max_length=1000, null=True, verbose_name="Candidate's position on this issue:"),
        ),
    ]