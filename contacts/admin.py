from django.contrib import admin
from .models import Contact, ContactList


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


@admin.register(ContactList)
class ContactListAdmin(admin.ModelAdmin):
    filter_horizontal = ['contacts']
    list_display = [
        'id',
        'name',
        'status',
        'date_created',
        'date_modified',
        'get_list_size',
    ]
    list_display_links = list_display
    list_filter = ['status']
    raw_id_fields = ['contacts']
    readonly_fields = [
        'date_created',
        'date_modified',
        'get_list_size',
    ]
    fields = readonly_fields + [
        'name',
        'status',
        'contacts',
    ]

    def get_list_size(self, obj):
        return obj.contacts.count()

    get_list_size.short_description = 'List Size'
