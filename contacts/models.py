# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.gis.db.models import PointField
from django.contrib.gis.db.models.functions import Distance
from django.db import models
from enum import Enum, unique
from phonenumber_field.modelfields import PhoneNumberField
import logging

logger = logging.getLogger(__name__)

name_max_length = 255
source_max_length = 255


def add_phone_opt_out(phone_number, opt_out_type, source):
    """
    Add Phone Opt Out for phone number string.

    Supports various standard phone number formats. Returns None if
    treat_as_none is True.

    Parameters
    ----------
    phone_number : str
        Phone number string to add to Opt Out list
    opt_out_type : OptOutType
        Opt Out Type to add
    source : str
        Source code for Opt Out

    Returns
        -------
        (PhoneOptOut, bool)
            Returns (Phone Opt Out, created) from get_or_create, or (None, False)
            https://docs.djangoproject.com/en/1.11/ref/models/querysets/#get-or-create
    """
    phone_opt_out, created = PhoneOptOut.objects.get_or_create(
        phone_number=phone_number,
        opt_out_type=opt_out_type.value[0],
        defaults={
            'phone_number': phone_number,
            'opt_out_type': opt_out_type.value[0],
            'source': source,
        },
    )
    if phone_opt_out is None or phone_opt_out.treat_as_none:
        return (None, False)
    else:
        return (phone_opt_out, created)


def find_phone_opt_out(phone_number, opt_out_type):
    """
    Find Phone Opt Out for phone number string

    Supports various standard phone number formats. Ignores match if
    treat_as_none is True.

    Parameters
    ----------
    phone_number : str
        Phone number string to search for
    opt_out_type : OptOutType
        Opt Out Type to search for

    Returns
        -------
        PhoneOptOut
            Returns matching Phone Opt Out, or None
    """

    phone_opt_out = PhoneOptOut.objects.filter(
        phone_number=phone_number,
        opt_out_type=opt_out_type.value[0],
    ).first()
    if phone_opt_out is None or phone_opt_out.treat_as_none:
        return None
    else:
        return phone_opt_out


def has_phone_opt_out(phone_number, opt_out_type):
    """
    Has Phone Opt Out for phone number string, or Not

    Mainly just a call to find_phone_opt_out method and converted to boolean

    Parameters
    ----------
    phone_number : str
        Phone number string to search for
    opt_out_type : OptOutType
        Opt Out Type to search for

    Returns
        -------
        bool
            Returns True for existing Phone Opt Out, or False
    """
    phone_opt_out = find_phone_opt_out(phone_number, opt_out_type)
    has_opt_out = phone_opt_out is not None
    return has_opt_out


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
        return '%s[%s]' % (
            (self.name + ' ' if self.name is not None else ''),
            str(self.id),
        )


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


@unique
class OptOutType(Enum):
    calling = (1, 'Calling')


class PhoneOptOut(models.Model):
    """
    Phone Opt Out Model

    Data for a specific Opt Out Type for a specific Phone Number
    """

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    opt_out_type = models.IntegerField(
        choices=[x.value for x in OptOutType],
        db_index=True,
        default=OptOutType.calling.value[0]
    )
    phone_number = PhoneNumberField(db_index=True)
    source = models.CharField(max_length=source_max_length)

    def __unicode__(self):
        return '%s %s [%s]' % (
            self.phone_number,
            self.get_opt_out_type_display(),
            str(self.id)
        )

    def _treat_as_none(self):
        """
        Treat as None. If this record is returned from search it is likely a
        false match.

        Returns
            -------
            bool
                Returns True if should treat as None, otherwise False
        """

        """Set list of None-like value"""
        none_list = [
            '',
            ' ',
            '+',
            'None',
            '+None',
            'NoneNone',
            '+NoneNone',  # This occurs for a lot of invalid numbers
        ]
        if str(self.phone_number) in none_list:
            return True
        else:
            return False
    treat_as_none = property(_treat_as_none)

    class Meta:
        unique_together = ["opt_out_type", "phone_number"]
