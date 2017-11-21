# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-11-18 00:22
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import wagtail.wagtailcore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0030_index_on_pagerevision_created_at'),
        ('wagtailimages', '0015_fill_filter_spec_field'),
        ('pages', '0045_auto_20171116_2250'),
    ]

    operations = [
        migrations.CreateModel(
            name='MicrositePage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
                ('button_background_color', models.CharField(blank=True, help_text='6 digit CSS color code.', max_length=6, null=True)),
                ('button_text', models.CharField(blank=True, max_length=128, null=True)),
                ('button_text_color', models.CharField(blank=True, help_text='6 digit CSS color code.', max_length=6, null=True)),
                ('button_url', models.URLField(blank=True, null=True)),
                ('button_url_new_window', models.BooleanField(default=False, help_text='Open new window for button url.')),
                ('custom_footer_background_color', models.CharField(blank=True, help_text='6 digit CSS color code.', max_length=6, null=True)),
                ('custom_footer_content', wagtail.wagtailcore.fields.RichTextField(blank=True, null=True)),
                ('custom_footer_show', models.BooleanField(default=False, help_text='Show custom footer.')),
                ('custom_footer_text_color', models.CharField(blank=True, help_text='6 digit CSS color code.', max_length=6, null=True)),
                ('custom_header_show', models.BooleanField(default=False, help_text='Show custom header with image, button, links etc.')),
                ('facebook_url', models.URLField(blank=True, null=True)),
                ('primary_content', wagtail.wagtailcore.fields.RichTextField()),
                ('primary_content_background_color', models.CharField(blank=True, help_text='6 digit CSS color code.', max_length=6, null=True)),
                ('primary_content_embed_code', models.TextField(blank=True, help_text='Raw HTML embed code for signup form, etc.', null=True)),
                ('primary_content_text_color', models.CharField(blank=True, help_text='6 digit CSS color code.', max_length=6, null=True)),
                ('secondary_content', wagtail.wagtailcore.fields.RichTextField(blank=True, null=True)),
                ('secondary_content_background_color', models.CharField(blank=True, help_text='6 digit CSS color code.', max_length=6, null=True)),
                ('secondary_content_show', models.BooleanField(default=False, help_text='Show secondary content.')),
                ('secondary_content_text_color', models.CharField(blank=True, help_text='6 digit CSS color code.', max_length=6, null=True)),
                ('standard_header_show', models.BooleanField(default=True, help_text='Show standard global header at top of page.')),
                ('standard_footer_show', models.BooleanField(default=True, help_text='Show standard global footer at bottom of page.')),
                ('twitter_url', models.URLField(blank=True, null=True)),
                ('custom_footer_background_image', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.Image')),
                ('custom_header_image', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.Image')),
                ('primary_content_background_image', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.Image')),
                ('secondary_content_background_image', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.Image')),
                ('social_image', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.Image')),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
    ]