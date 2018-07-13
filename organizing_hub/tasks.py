# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
import logging


logger = logging.getLogger(__name__)


@shared_task
def lebowski(x, y):
    for number in range(0, 100000):
        logger.debug(number)

    return x + y


@shared_task
def add(x, y):
    return x + y


@shared_task
def mul(x, y):
    return x * y


@shared_task
def xsum(numbers):
    return sum(numbers)
