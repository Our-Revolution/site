# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2018-04-27 16:13
from __future__ import unicode_literals

from django.db import migrations
import wagtail.wagtailcore.fields
import wagtail.wagtaildocs.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0065_auto_20180426_1611'),
    ]

    operations = [
        migrations.AddField(
            model_name='donationpage',
            name='csv_files',
            field=wagtail.wagtailcore.fields.StreamField([('csv_file', wagtail.wagtaildocs.blocks.DocumentChooserBlock())], default=''),
            preserve_default=False,
        ),
    ]
