# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-08-16 23:47
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailimages', '0019_delete_filter'),
        ('birthday_pages', '0007_auto_20180816_2345'),
    ]

    operations = [
        migrations.AddField(
            model_name='birthdaypage',
            name='header_background_image',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.Image'),
        ),
    ]
