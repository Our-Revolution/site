# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-08-08 04:00
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('calls', '0002_auto_20180808_0340'),
    ]

    operations = [
        migrations.AddField(
            model_name='call',
            name='date_modified',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='callcampaign',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='callcampaign',
            name='date_modified',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='callprofile',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='callprofile',
            name='date_modified',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='callresponse',
            name='date_modified',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='callresponse',
            name='question',
            field=models.IntegerField(choices=[(1, 'Opt out of future calls?'), (2, 'Did the contact pick up the phone?'), (3, 'Does the contact want to take action with your group?')]),
        ),
    ]
