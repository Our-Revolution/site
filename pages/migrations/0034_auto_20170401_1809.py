# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-04-01 18:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0033_auto_20170306_2240'),
    ]

    operations = [
        migrations.AlterField(
            model_name='youtubepage',
            name='youtube_video_id',
            field=models.CharField(max_length=30),
        ),
    ]