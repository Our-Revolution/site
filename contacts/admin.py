from django.contrib import admin
from .models import Contact, ContactList


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    readonly_fields = [
        'date_created',
        'date_modified',
    ]
    fields = readonly_fields + [
        'external_id',
        'first_name',
        'last_name',
        'email_address',
        'phone_number',
        'point',
    ]


@admin.register(ContactList)
class ContactListAdmin(admin.ModelAdmin):
    filter_horizontal = ['contacts']
    readonly_fields = [
        'date_created',
        'date_modified',
    ]
    fields = readonly_fields + [
        'name',
        'status',
        'contacts',
    ]
