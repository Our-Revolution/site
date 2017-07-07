# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-07-07 20:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nominations', '0027_auto_20170707_2044'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='vol_advantage',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Previous Election D% or R% Advantage:'),
        ),
        migrations.AddField(
            model_name='application',
            name='vol_crimes',
            field=models.TextField(blank=True, max_length=500, null=True, verbose_name='Crimes or Scandals (please add links to source):'),
        ),
        migrations.AddField(
            model_name='application',
            name='vol_dem_challenger',
            field=models.NullBooleanField(verbose_name='If primary, who are the Democratic challengers?'),
        ),
        migrations.AddField(
            model_name='application',
            name='vol_endorsements',
            field=models.TextField(blank=True, max_length=500, null=True, verbose_name='Endorsements:'),
        ),
        migrations.AddField(
            model_name='application',
            name='vol_fundraising',
            field=models.IntegerField(blank=True, null=True, verbose_name='How much money fundraised?'),
        ),
        migrations.AddField(
            model_name='application',
            name='vol_notes',
            field=models.TextField(blank=True, max_length=500, null=True, verbose_name='Notes:'),
        ),
        migrations.AddField(
            model_name='application',
            name='vol_opponent_fundraising',
            field=models.IntegerField(blank=True, null=True, verbose_name='How much competitors have fundraised?'),
        ),
        migrations.AddField(
            model_name='application',
            name='vol_other_progressives',
            field=models.TextField(blank=True, max_length=500, null=True, verbose_name='Other progressives running:'),
        ),
        migrations.AddField(
            model_name='application',
            name='vol_polling',
            field=models.TextField(blank=True, max_length=500, null=True, verbose_name='Polling:'),
        ),
        migrations.AddField(
            model_name='application',
            name='vol_turnout',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name='Previous Election Year Turnout:'),
        ),
        migrations.AddField(
            model_name='application',
            name='vol_win_number',
            field=models.IntegerField(blank=True, null=True, verbose_name='Win Number:'),
        ),
    ]
