# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf.urls import url
from django.contrib import admin
from .admin_views import PhoneOptOutUploadView
from .models import Contact, ContactList, PhoneOptOut


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    readonly_fields = [
        'point',
        'date_created',
        'date_modified',
    ]
    fields = readonly_fields + [
        'external_id',
        'first_name',
        'last_name',
        'email_address',
        'phone_number',
    ]
    search_fields = [
        'email_address',
        'external_id',
        'first_name',
        'id',
        'last_name'
    ]


@admin.register(ContactList)
class ContactListAdmin(admin.ModelAdmin):
    filter_horizontal = ['contacts']
    list_display = [
        'id',
        'name',
        'status',
        'get_list_size',
        'date_created',
        'date_modified',
    ]
    list_display_links = list_display
    list_filter = ['status']
    raw_id_fields = ['contacts']
    readonly_fields = [
        'get_list_size',
        'date_created',
        'date_modified',
    ]
    fields = readonly_fields + [
        'name',
        'status',
        'contacts',
    ]

    def get_list_size(self, obj):
        return obj.contacts.count()

    get_list_size.short_description = 'List Size'


@admin.register(PhoneOptOut)
class PhoneOptOutAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'phone_number',
        'opt_out_type',
        'source',
        'date_created',
    ]
    list_display_links = list_display

    readonly_fields = ['date_created', 'date_modified']
    fields = readonly_fields + ['phone_number', 'opt_out_type', 'source']

    def get_urls(self):
        urls = super(PhoneOptOutAdmin, self).get_urls()
        my_urls = [
            url(
                r'^upload/',
                PhoneOptOutUploadView.as_view(),
            ),
        ]
        return my_urls + urls
