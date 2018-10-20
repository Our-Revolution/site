# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from contacts.models import add_phone_opt_out, OptOutType
from .models import CallAnswer, CallQuestion, CallResponse
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=CallResponse)
def call_response_post_save_handler(instance, **kwargs):

    call_response = instance

    """Check if Call Response indicated Opt Out Request"""
    if call_response.question == CallQuestion.opt_out.value[0] and (
        call_response.answer == CallAnswer.yes.value[0]
    ):
        """Add Phone Opt Out for Contact phone number"""
        call = call_response.call
        contact = call.contact
        if contact.phone_number is not None:
            timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
            source = 'Call Response: %s | Contact: %s | %s' % (
                str(call_response.id),
                str(contact.id),
                timestamp,
            )
            transaction.on_commit(
                lambda: add_phone_opt_out(
                    contact.phone_number,
                    OptOutType.calling,
                    source,
                )
            )
