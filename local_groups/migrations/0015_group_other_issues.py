# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-03-02 18:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('local_groups', '0014_auto_20170302_1813'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='other_issues',
            field=models.TextField(blank=True, null=True),
        ),
    ]