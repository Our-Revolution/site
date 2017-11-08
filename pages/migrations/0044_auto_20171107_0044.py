# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-11-07 00:44
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0030_index_on_pagerevision_created_at'),
        ('pages', '0043_notificationbanner'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidaterace',
            name='candidate_endorsement_page',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='wagtailcore.Page'),
        ),
        migrations.AddField(
            model_name='initiativerace',
            name='initiative_endorsement_page',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='wagtailcore.Page'),
        ),
    ]