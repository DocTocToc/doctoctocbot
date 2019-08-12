from __future__ import absolute_import, unicode_literals
from celery import shared_task
import logging

logger = logging.getLogger(__name__)

@shared_task
def test_task():
    logger.debug("*** test_tak started ***")
    i = 0
    while i < 3:
        i+=1
        logger.debug("*** test_task is running ***")
