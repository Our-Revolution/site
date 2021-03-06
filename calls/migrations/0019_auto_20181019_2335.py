# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-10-19 23:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calls', '0018_auto_20181017_2359'),
    ]

    operations = [
        migrations.AlterField(
            model_name='callresponse',
            name='question',
            field=models.IntegerField(choices=[(1, 'Did you talk to the contact?'), (2, 'If you did not talk to the contact, why not?'), (3, 'Did the contact want to take action?'), (4, 'Did you leave a voice message?'), (5, 'Did you send a text message?'), (6, 'Did the contact want to opt out?')]),
        ),
    ]
