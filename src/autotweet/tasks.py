from __future__ import absolute_import, unicode_literals
import logging

from celery import shared_task

from constance import config

from community.models import Community

logger = logging.getLogger(__name__)