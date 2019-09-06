from __future__ import absolute_import, unicode_literals

from celery import shared_task

import logging
import requests
from pathlib import Path

logger = logging.getLogger(__name__)

@shared_task
def handle_retweetroot(statusid: int):
    from .bin.thread import retweetroot
    retweetroot(statusid)
    
@shared_task(bind=True)
def handle_question(self, statusid: int):
    from .bin.thread import question
    ok = question(statusid) 
    if not ok:
        self.retry(args=(statusid,), countdown=2 ** self.request.retries, max_retries=10)
        
@shared_task
def handle_on_status(statusid: int):
    from .onstatus import triage
    logger.info("handling status %d" % statusid)
    triage(statusid)
    
@shared_task
def handle_retweet(statusid: int):
    from bot.doctoctocbot import retweet
    retweet(statusid)

@shared_task
def handle_image(url, filepath):
    r = requests.get(url, allow_redirects=True)
    with open(filepath, 'wb') as f:
        f.write(r.content)
    file = Path(filepath)
    if file.is_file():
        logger.info("Image %s written on disk." % filepath)
    else:
        logger.error("Image %s not found on disk." % filepath)