# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
import logging


logger = logging.getLogger(__name__)


"""TODO: remove lebowski when done testing"""


@shared_task
def lebowski(x, y):
    for number in range(0, 100000):
        logger.debug(number)

    return x + y
