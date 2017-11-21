# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-11-21 00:50
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailimages', '0015_fill_filter_spec_field'),
        ('pages', '0048_micrositepage_custom_header_background_color'),
    ]

    operations = [
        migrations.AddField(
            model_name='micrositepage',
            name='custom_favicon',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.Image'),
        ),
    ]