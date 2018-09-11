# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-09-07 01:23
from __future__ import unicode_literals

from django.db import migrations
import uuid


def gen_uuid(apps, schema_editor):
    CallCampaign = apps.get_model('calls', 'CallCampaign')
    for row in CallCampaign.objects.all():
        row.uuid = uuid.uuid4()
        row.save(update_fields=['uuid'])


class Migration(migrations.Migration):

    dependencies = [
        ('calls', '0008_callcampaign_uuid'),
    ]

    operations = [
        # omit reverse_code=... if you don't want the migration to be reversible.
        migrations.RunPython(gen_uuid, reverse_code=migrations.RunPython.noop),
    ]
