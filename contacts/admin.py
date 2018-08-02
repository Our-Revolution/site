from django.contrib import admin
from .models import Contact, ContactList


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    pass


@admin.register(ContactList)
class ContactListAdmin(admin.ModelAdmin):
    pass
