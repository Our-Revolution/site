from __future__ import unicode_literals
from django.conf import settings
from django.db import models
import logging

logger = logging.getLogger(__name__)

EVENTS_DEFAULT_FROM_NAME = settings.EVENTS_DEFAULT_FROM_NAME
EVENTS_DEFAULT_SUBJECT = settings.EVENTS_DEFAULT_SUBJECT


class EventPromotionRecipient(models.Model):
    """Assume unique external user id for Recipient"""
    user_external_id = models.CharField(max_length=128, unique=True)


class EventPromotion(models.Model):
    status_choices = (
        (1, 'New'),
        (2, 'Approved'),
        (3, 'Sent'),
        (4, 'Skipped'),
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
    recipients = models.ManyToManyField(
        EventPromotionRecipient,
        blank=True,
    )
    sender_display_name = models.CharField(
        default=EVENTS_DEFAULT_FROM_NAME,
        max_length=128
    )
    status = models.IntegerField(choices=status_choices, default=1)
    subject = models.CharField(default=EVENTS_DEFAULT_SUBJECT, max_length=128)
    """Assume generic external user id for event owner/host"""
    user_external_id = models.CharField(db_index=True, max_length=128)
