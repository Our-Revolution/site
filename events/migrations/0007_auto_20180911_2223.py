# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-09-11 22:23
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0006_auto_20180910_2148'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventpromotion',
            name='contact_list',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='contacts.ContactList'),
        ),
    ]