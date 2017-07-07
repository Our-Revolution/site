# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-07-07 20:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nominations', '0024_questionnaire_candidate_bio'),
    ]

    operations = [
        migrations.AddField(
            model_name='questionnaire',
            name='candidate_held_office',
            field=models.NullBooleanField(verbose_name='Has the candidate ever held public office?'),
        ),
        migrations.AddField(
            model_name='questionnaire',
            name='candidate_party',
            field=models.CharField(max_length=255, null=True, verbose_name='Candidate Party Affiliation'),
        ),
        migrations.AlterField(
            model_name='questionnaire',
            name='candidate_bio',
            field=models.TextField(max_length=1000, verbose_name='Candidate Bio'),
        ),
    ]
