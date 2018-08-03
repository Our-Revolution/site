from __future__ import unicode_literals
from django.conf import settings
from django.db import models
from contacts.models import Contact, ContactList
import logging

logger = logging.getLogger(__name__)

EVENTS_DEFAULT_FROM_NAME = settings.EVENTS_DEFAULT_FROM_NAME
EVENTS_DEFAULT_SUBJECT = settings.EVENTS_DEFAULT_SUBJECT

"""Event Promotion statuses"""
event_promotion_status_new = 1
event_promotion_status_approved = 10
event_promotion_status_sent = 20
event_promotion_status_skipped = 30
event_promotion_status_choices = (
    (event_promotion_status_new, 'New'),
    (event_promotion_status_approved, 'Approved'),
    (event_promotion_status_sent, 'Sent'),
    (event_promotion_status_skipped, 'Skipped'),
)


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
        status=event_promotion_status_sent,
        contact_list__contacts=contact
    ).order_by('-date_sent').first()

    return last_event_promo_sent


class EventPromotion(models.Model):

    contact_list = models.ForeignKey(
        ContactList,
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
    message = models.CharField(max_length=2048)
    sender_display_name = models.CharField(
        default=EVENTS_DEFAULT_FROM_NAME,
        max_length=128
    )
    status = models.IntegerField(
        choices=event_promotion_status_choices,
        default=event_promotion_status_new
    )
    subject = models.CharField(default=EVENTS_DEFAULT_SUBJECT, max_length=128)
    """Assume generic external user id for event owner/host"""
    user_external_id = models.CharField(db_index=True, max_length=128)

    def __unicode__(self):
        return str(self.id) + " | Event: " + self.event_external_id + " | User: " + self.user_external_id + (
            " | " + self.event_name if self.event_name else ""
        )

    class Meta:
        ordering = [
            "-date_submitted",
        ]
