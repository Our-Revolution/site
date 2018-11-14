# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from celery import Task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

ADMINS = settings.ADMINS
DEBUG = settings.DEBUG
SERVER_EMAIL = settings.SERVER_EMAIL


class BaseTask(Task):

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        if not DEBUG:
            subject = "[Django] ERROR: Task Fail: %s [%s]" % (task_id, exc)
            text_content = "[Django] ERROR: Task Fail: %s [%s] [%s] [%s]" % (
                task_id,
                exc,
                timezone.now(),
                einfo,
            )
            html_content = text_content
            msg = EmailMultiAlternatives(
                subject,
                text_content,
                SERVER_EMAIL,
                [a[1] for a in ADMINS],
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
