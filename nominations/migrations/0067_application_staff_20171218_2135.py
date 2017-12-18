# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-12-18 21:35
from __future__ import unicode_literals

from django.db import migrations, models


# Update all legacy data to fit new format
def update_application_staff_data(apps, schema_editor):
    Application = apps.get_model('nominations', 'Application')
    for application in Application.objects.all():
        if application.staff == "1":
            application.staff = "Erika Andiola"
            application.save()


class Migration(migrations.Migration):

    dependencies = [
        ('nominations', '0066_auto_20171212_1747'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='staff',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.RunPython(update_application_staff_data),
    ]
