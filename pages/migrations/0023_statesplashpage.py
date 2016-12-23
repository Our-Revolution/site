# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-12-23 19:46
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import wagtail.wagtailcore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0030_index_on_pagerevision_created_at'),
        ('wagtailimages', '0015_fill_filter_spec_field'),
        ('pages', '0022_auto_20161213_1741'),
    ]

    operations = [
        migrations.CreateModel(
            name='StateSplashPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
                ('abstract', wagtail.wagtailcore.fields.RichTextField()),
                ('body', wagtail.wagtailcore.fields.RichTextField(blank=True, null=True)),
                ('social_image', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.Image')),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
    ]
