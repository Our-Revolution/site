from __future__ import unicode_literals
from django.contrib.gis.db.models import PointField
from django.contrib.gis.db.models.functions import Distance
from django.db import models
from enum import Enum, unique
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


@unique
class ContactListStatus(Enum):
    new = (1, 'New')
    in_progress = (10, 'In Progress (building list)')
    complete = (20, 'Complete (ready to use)')


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
        choices=[x.value for x in ContactListStatus],
        default=ContactListStatus.new.value[0]
    )

    def __unicode__(self):
        return '%s: %s' % (self.id, self.name)

    def trim_list_by_distance(self, list_limit, point):
        """
        Trim contact list by distance

        Parameters
        ----------
        self : ContactList
            ContactList to trim
        list_limit : int
            Size limit for list
        point : Point
            Point to use for distance sorting

        Returns
            -------
            ContactList
                Returns updated ContactList
        """

        """If list size is greater than limit, then trim by distance"""
        if self.contacts.count() > list_limit:

            """Sort contacts by distance to point"""
            contacts_sorted = self.contacts.annotate(
                distance=Distance('point', point)
            ).order_by('distance')

            """Slice sorted list to get extras above limit"""
            contacts_extra = contacts_sorted[list_limit:]

            """Remove extras from contact list"""
            self.contacts.remove(*contacts_extra)

        return self
