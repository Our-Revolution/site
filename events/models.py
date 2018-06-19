from __future__ import unicode_literals
from django.db import models
import logging

logger = logging.getLogger(__name__)


class EventPromotionRecipient(models.Model):
    user_external_id = models.CharField(max_length=128)


class EventPromotionRequest(models.Model):
    status_choices = (
        (1, 'New'),
        (2, 'Approved'),
        (3, 'Sent'),
        (4, 'Skipped'),
    )

    date_sent = models.DateTimeField(null=True, blank=True)
    event_external_id = models.CharField(max_length=128)
    message = models.CharField(max_length=2048)
    recipients = models.ManyToManyField(
        EventPromotionRecipient,
        blank=True,
    )
    sender_display_name = models.CharField(max_length=128, null=True)
    sender_email = models.EmailField(null=True)
    status = models.IntegerField(choices=status_choices, default=1)
    subject = models.CharField(max_length=128)
    submitted = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    user_external_id = models.CharField(max_length=128)
    volunteer_count = models.IntegerField()
