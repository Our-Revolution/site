from __future__ import unicode_literals
from django.contrib.gis.db.models import PointField
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
import logging

logger = logging.getLogger(__name__)

"""Contact List statuses"""
contact_list_status_new = 1
contact_list_status_in_progress = 10
contact_list_status_complete = 20
contact_list_status_choices = (
    (contact_list_status_new, 'New'),
    (contact_list_status_in_progress, 'In Progress (building list)'),
    (contact_list_status_complete, 'Complete (ready to use)'),
)

name_max_length = 255


class Contact(models.Model):
    """
    Contact Model

    This is meant to be a basic flexible contact model with lots of optional
    fields for use with CRM-like features
    """

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    email_address = models.EmailField(
        blank=True,
        max_length=255,
        null=True,
    )
    external_id = models.CharField(
        blank=True,
        max_length=128,
        null=True,
        unique=True,
    )
    first_name = models.CharField(
        blank=True,
        max_length=name_max_length,
        null=True,
    )
    last_name = models.CharField(
        blank=True,
        max_length=name_max_length,
        null=True,
    )
    phone_number = PhoneNumberField(blank=True, null=True)
    point = PointField(blank=True, null=True)

    def _name(self):
        if self.first_name and self.last_name:
            return self.first_name + ' ' + self.last_name
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return None
    name = property(_name)

    def __unicode__(self):
        return str(self.id) + (' ' + self.name if self.name else '')


class ContactList(models.Model):
    """
    Contact List Model

    List of Contacts plus information about the list itself
    """

    contacts = models.ManyToManyField(Contact, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=name_max_length)
    status = models.IntegerField(
        choices=contact_list_status_choices,
        default=contact_list_status_new
    )

    def __unicode__(self):
        return '%s: %s' % (self.id, self.name)
