# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-06-26 19:13
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nominations', '0081_application_staff_recommendation'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='application',
            options={'permissions': (('bulk_change_application_status', 'Can bulk change status of applications'), ('export_pdf_application', 'Can export to pdf'), ('admin_application', 'Can admin override application data')), 'verbose_name': 'Candidate Application'},
        ),
    ]
