from django.contrib import admin
from .models import Contact, ContactList


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    readonly_fields = [
        'external_id',
        'first_name',
        'last_name',
        'email_address',
        'phone_number',
        'point',
        'date_created',
        'date_modified',
    ]


@admin.register(ContactList)
class ContactListAdmin(admin.ModelAdmin):
    readonly_fields = [
        'name',
        'status',
        'contacts',
        'date_created',
        'date_modified',
    ]
