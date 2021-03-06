# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-08-15 22:36
from __future__ import unicode_literals

from django.db import migrations
import wagtail.wagtailcore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('birthday_pages', '0005_auto_20180814_0318'),
    ]

    operations = [
        migrations.AlterField(
            model_name='birthdaypage',
            name='section_2_1_body',
            field=wagtail.wagtailcore.fields.RichTextField(help_text='Use bold for large text.'),
        ),
        migrations.AlterField(
            model_name='birthdaypage',
            name='section_2_2_body',
            field=wagtail.wagtailcore.fields.RichTextField(help_text='Use bold for large text.'),
        ),
        migrations.AlterField(
            model_name='birthdaypage',
            name='section_2_3_body',
            field=wagtail.wagtailcore.fields.RichTextField(help_text='Use bold for large text.'),
        ),
        migrations.AlterField(
            model_name='birthdaypage',
            name='section_2_4_body',
            field=wagtail.wagtailcore.fields.RichTextField(help_text='Use bold for large text.'),
        ),
    ]
