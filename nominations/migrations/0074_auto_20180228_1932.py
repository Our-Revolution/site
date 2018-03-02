# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2018-02-28 19:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nominations', '0073_application_primary_election_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='fundraising_date_accessed',
            field=models.DateField(blank=True, null=True, verbose_name='Date that fundraising information was accessed'),
        ),
        migrations.AddField(
            model_name='application',
            name='fundraising_date_of_filing',
            field=models.DateField(blank=True, null=True, verbose_name='Filing date for Campaign Finance Report'),
        ),
        migrations.AddField(
            model_name='application',
            name='fundraising_source_url',
            field=models.URLField(blank=True, max_length=255, null=True, verbose_name='Source URL for Campaign Finance Report'),
        ),
        migrations.AddField(
            model_name='applicationcandidate',
            name='fundraising',
            field=models.IntegerField(blank=True, null=True, verbose_name='Cash on Hand'),
        ),
    ]