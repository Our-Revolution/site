from __future__ import unicode_literals
from django.conf import settings
from django.db import models
from enum import Enum, unique
from contacts.models import Contact, ContactList
import logging

logger = logging.getLogger(__name__)

EVENTS_DEFAULT_FROM_NAME = settings.EVENTS_DEFAULT_FROM_NAME
EVENTS_DEFAULT_SUBJECT = settings.EVENTS_DEFAULT_SUBJECT

"""Keep message short or else it will break call to BSD api"""
message_max_length = 2048


def find_last_event_promo_sent_to_contact(contact_external_id):
    """
    Find most recent Event Promotion sent to Contact based on external id

    Parameters
    ----------
    contact_external_id : str
        Contact external_id field

    Returns
        -------
        EventPromotion
            Returns matching Event Promotion, or None
    """

    """See if there is a matching contact"""
    contact = Contact.objects.filter(external_id=contact_external_id).first()
    if contact is None:
        return None

    """Find last event promo sent to contact"""
    last_event_promo_sent = EventPromotion.objects.filter(
        status=EventPromotionStatus.sent.value[0],
        contact_list__contacts=contact
    ).order_by('-date_sent').first()

    return last_event_promo_sent


@unique
class EventPromotionStatus(Enum):
    new = (1, 'New')
    approved = (10, 'Approved')
    in_progress = (20, 'In Progress')
    sent = (30, 'Sent')
    skipped = (40, 'Skipped')
    event_not_approved = (50, 'Event Not Approved')
    expired = (60, 'Expired')

"""Statuses that require clearing of the contact list"""
event_promotion_statuses_for_list_clear = [
    EventPromotionStatus.skipped,
    EventPromotionStatus.event_not_approved,
    EventPromotionStatus.expired
]

class EventPromotion(models.Model):

    contact_list = models.OneToOneField(
        ContactList,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    date_sent = models.DateTimeField(null=True)
    date_submitted = models.DateTimeField(null=True, auto_now_add=True)
    """Assume generic external event id"""
    event_external_id = models.CharField(db_index=True, max_length=128)
    """Optional event name for convenience"""
    event_name = models.CharField(
        blank=True,
        max_length=128,
        null=True,
    )
    max_recipients = models.IntegerField()
    message = models.CharField(max_length=message_max_length)
    sender_display_name = models.CharField(
        default=EVENTS_DEFAULT_FROM_NAME,
        max_length=128
    )
    status = models.IntegerField(
        choices=[x.value for x in EventPromotionStatus],
        default=EventPromotionStatus.new.value[0]
    )
    subject = models.CharField(default=EVENTS_DEFAULT_SUBJECT, max_length=128)
    """Assume generic external user id for event owner/host"""
    user_external_id = models.CharField(db_index=True, max_length=128)

    def _requires_list_clear(self):
        """Check if status is in list of statuses that requires a list clear"""
        return self.status in [
            x.value[0] for x in event_promotion_statuses_for_list_clear
        ]
    requires_list_clear = property(_requires_list_clear)

    def __unicode__(self):
        return str(self.id) + " | Event: " + self.event_external_id + " | User: " + self.user_external_id + (
            " | " + self.event_name if self.event_name else ""
        )

    class Meta:
        ordering = [
            "-date_submitted",
        ]
