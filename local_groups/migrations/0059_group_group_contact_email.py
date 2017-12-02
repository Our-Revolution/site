# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-11-30 01:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('local_groups', '0058_group_notes'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='group_contact_email',
            field=models.EmailField(blank=True, help_text='Optional Group Contact Email to publicly display an email\n        different from Individual Contact Email', max_length=254, null=True),
        ),
    ]