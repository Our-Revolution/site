# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-02-08 05:20
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailforms', '0003_capitalizeverbose'),
        ('wagtailcore', '0030_index_on_pagerevision_created_at'),
        ('wagtailredirects', '0005_capitalizeverbose'),
        ('pages', '0029_merge_20170208_0320'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='donorlistpage',
            name='page_ptr',
        ),
        migrations.RemoveField(
            model_name='donorlistpage',
            name='social_image',
        ),
        migrations.DeleteModel(
            name='DonorListPage',
        ),
    ]