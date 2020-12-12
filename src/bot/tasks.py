from __future__ import absolute_import, unicode_literals

from celery import shared_task

import logging
import requests
import random
import time
from pathlib import Path

logger = logging.getLogger(__name__)

@shared_task
def handle_retweetroot(statusid: int):
    from .bin.thread import retweetroot
    retweetroot(statusid)
    
@shared_task
def handle_question(statusid: int):
    from bot.bin.thread import question_api
    for i in range(1,5):
        ok = question_api(statusid)
        if ok:
            break
        else:
            time.sleep(30*2**i)

        
@shared_task
def handle_on_status(json: dict, community: str):
    from bot.onstatus import triage
    logger.info(f"handling status {json} for community {community}")
    triage(json=json, community=community)
    
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