# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-12-06 02:17
from __future__ import unicode_literals

from django.db import migrations
import wagtail.wagtailcore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0051_groupresourcepage_sub_heading'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groupresourcepage',
            name='body',
            field=wagtail.wagtailcore.fields.RichTextField(help_text='\n        All H# tags will be automatically converted to a table of contents.\n        '),
        ),
    ]
