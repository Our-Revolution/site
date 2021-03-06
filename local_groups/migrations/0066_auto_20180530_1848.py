# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2018-05-30 18:48
from __future__ import unicode_literals

from django.db import migrations


"""Insert 2 roles to start"""
initial_role_types = [1, 2]


def forwards_func(apps, schema_editor):
    # We get the model from the versioned app registry;
    # if we directly import it, it'll be the wrong version
    LocalGroupRole = apps.get_model("local_groups", "LocalGroupRole")
    db_alias = schema_editor.connection.alias
    for role_type in initial_role_types:
        LocalGroupRole.objects.using(db_alias).create(role_type=role_type)


def reverse_func(apps, schema_editor):
    # forwards_func() creates initial LocalGroupRole instances,
    # so reverse_func() should delete them.
    LocalGroupRole = apps.get_model("local_groups", "LocalGroupRole")
    db_alias = schema_editor.connection.alias
    for role_type in initial_role_types:
        LocalGroupRole.objects.using(db_alias).filter(
            role_type=role_type
        ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('local_groups', '0065_auto_20180530_1846'),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ]
