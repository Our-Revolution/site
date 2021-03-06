# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-25 18:32
from __future__ import unicode_literals
from django.db import migrations


def populate_stop_tpp_now_page(apps, schema_editor):
    from pages.models import IndexPage, TemplatePage
    home_page = IndexPage.objects.get(title='Our Revolution')
    stop_tpp_now_page = TemplatePage(title='Stop TPP Now', slug='stop-tpp-now', template='pages/stop_tpp_now.html')
    home_page.add_child(instance=stop_tpp_now_page)


def remove_stop_tpp_now_page(apps, schema_editor):
    from pages.models import TemplatePage
    TemplatePage.objects.get(title='Stop TPP Now').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0013_populate_take_action'),
    ]

    operations = [
        migrations.RunPython(populate_stop_tpp_now_page, reverse_code=remove_stop_tpp_now_page)
    ]
