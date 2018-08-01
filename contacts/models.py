from __future__ import unicode_literals
from django.contrib.gis.db.models import PointField
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
import logging

logger = logging.getLogger(__name__)

name_max_length = 255


class Contact(models.Model):
    """
    Contact Model

    This is meant to be a basic flexible contact model with lots of optional
    fields for use with CRM-like features
    """

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
    status_choices = (
        (1, 'New'),
        (10, 'List build in progress'),
        (20, 'List complete'),
    )
    status_new = 1

    contacts = models.ManyToManyField(Contact, blank=True)
    name = models.CharField(max_length=name_max_length)
    status = models.IntegerField(choices=status_choices, default=status_new)

    def __unicode__(self):
        return self.name
