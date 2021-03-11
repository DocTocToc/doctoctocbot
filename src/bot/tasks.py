from __future__ import absolute_import, unicode_literals

import logging
import requests
import time
from pathlib import Path

from django.conf import settings

from celery import shared_task

logger = logging.getLogger(__name__)

@shared_task
def handle_retweetroot(statusid: int):
    from .bin.thread import retweetroot
    retweetroot(statusid)
    
@shared_task
def handle_question(statusid: int):
    from bot.bin.thread import question_api
    for i in range(1,8):
        logger.info(f"handle_question statusid: {statusid}, loop: {i}")
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
def handle_image(url, filename):
    for name in ["thumb", "large"]:
        if name == "thumb":
            filepath = settings.BOT_IMAGES_THUMBNAILS_PATH + "/" + filename
        elif name == "large":
            filepath = settings.BOT_IMAGES_PATH + "/" + filename
        full_url = url + f"?name={name}"
        r = requests.get(full_url, allow_redirects=True)
        with open(filepath, 'wb') as f:
            f.write(r.content)
        file = Path(filepath)
        if file.is_file():
            logger.debug(f"{name} image %s written on disk." % filepath)
        else:
            logger.error(f"{name} image %s not found on disk." % filepath)