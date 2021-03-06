# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-07-30 21:41
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0002_contactlist'),
        ('events', '0004_auto_20180724_2359'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='eventpromotion',
            name='recipients',
        ),
        migrations.AddField(
            model_name='eventpromotion',
            name='contact_list',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='contacts.ContactList'),
        ),
        migrations.AlterField(
            model_name='eventpromotion',
            name='status',
            field=models.IntegerField(choices=[(1, 'New'), (10, 'Approved'), (20, 'Sent'), (30, 'Skipped')], default=1),
        ),
    ]
