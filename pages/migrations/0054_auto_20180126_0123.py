# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2018-01-26 01:23
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailimages', '0015_fill_filter_spec_field'),
        ('pages', '0053_auto_20180116_2153'),
    ]

    operations = [
        migrations.AddField(
            model_name='indexpage',
            name='block_1_background_color',
            field=models.CharField(default='218fff', help_text='6 digit CSS color code.', max_length=6),
        ),
        migrations.AddField(
            model_name='indexpage',
            name='block_1_background_image',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.Image'),
        ),
        migrations.AddField(
            model_name='indexpage',
            name='block_1_button_color',
            field=models.CharField(blank=True, choices=[('green', 'Green'), ('blue', 'Blue'), ('red', 'Red')], max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='indexpage',
            name='block_1_button_text',
            field=models.CharField(blank=True, max_length=16, null=True),
        ),
        migrations.AddField(
            model_name='indexpage',
            name='block_1_button_url',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='indexpage',
            name='block_1_button_url_new_window',
            field=models.BooleanField(default=False, help_text='Open new window for button url.'),
        ),
        migrations.AddField(
            model_name='indexpage',
            name='block_1_embed_code',
            field=models.TextField(blank=True, help_text='Raw HTML embed code for video, etc.', null=True),
        ),
        migrations.AddField(
            model_name='indexpage',
            name='block_1_text',
            field=models.CharField(blank=True, max_length=140, null=True),
        ),
        migrations.AddField(
            model_name='indexpage',
            name='block_2_background_color',
            field=models.CharField(default='218fff', help_text='6 digit CSS color code.', max_length=6),
        ),
        migrations.AddField(
            model_name='indexpage',
            name='block_2_background_image',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.Image'),
        ),
        migrations.AddField(
            model_name='indexpage',
            name='block_2_button_color',
            field=models.CharField(blank=True, choices=[('green', 'Green'), ('blue', 'Blue'), ('red', 'Red')], max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='indexpage',
            name='block_2_button_text',
            field=models.CharField(blank=True, max_length=16, null=True),
        ),
        migrations.AddField(
            model_name='indexpage',
            name='block_2_button_url',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='indexpage',
            name='block_2_button_url_new_window',
            field=models.BooleanField(default=False, help_text='Open new window for button url.'),
        ),
        migrations.AddField(
            model_name='indexpage',
            name='block_2_embed_code',
            field=models.TextField(blank=True, help_text='Raw HTML embed code for video, etc.', null=True),
        ),
        migrations.AddField(
            model_name='indexpage',
            name='block_2_text',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='indexpage',
            name='block_3_background_color',
            field=models.CharField(default='218fff', help_text='6 digit CSS color code.', max_length=6),
        ),
        migrations.AddField(
            model_name='indexpage',
            name='block_3_background_image',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.Image'),
        ),
        migrations.AddField(
            model_name='indexpage',
            name='block_3_button_color',
            field=models.CharField(blank=True, choices=[('green', 'Green'), ('blue', 'Blue'), ('red', 'Red')], max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='indexpage',
            name='block_3_button_text',
            field=models.CharField(blank=True, max_length=16, null=True),
        ),
        migrations.AddField(
            model_name='indexpage',
            name='block_3_button_url',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='indexpage',
            name='block_3_button_url_new_window',
            field=models.BooleanField(default=False, help_text='Open new window for button url.'),
        ),
        migrations.AddField(
            model_name='indexpage',
            name='block_3_embed_code',
            field=models.TextField(blank=True, help_text='Raw HTML embed code for video, etc.', null=True),
        ),
        migrations.AddField(
            model_name='indexpage',
            name='block_3_text',
            field=models.CharField(blank=True, max_length=60, null=True),
        ),
    ]
