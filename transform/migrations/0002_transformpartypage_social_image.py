# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2018-03-16 04:25
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailimages', '0015_fill_filter_spec_field'),
        ('transform', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='transformpartypage',
            name='social_image',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.Image'),
        ),
    ]