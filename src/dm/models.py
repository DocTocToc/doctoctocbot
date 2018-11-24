from django.db import models
from django.contrib.postgres.fields import JSONField
from django.utils.translation import gettext_lazy as _

import logging
from django.contrib.admin.utils import help_text_for_field
logger = logging.getLogger(__name__)


from bot.conf.cfg import getConfig
from common.utils import dictextract 

class DirectMessageManager(models.Manager):
    def createdm(self, **kwargs):
        logger.debug(f"kwargs: {kwargs}")
        keys = ["id", "created_timestamp", "sender_id", "recipient_id", "source_app_id", "text"]
        d = {}
        for key in keys:
            try:
                value = next(dictextract(key, kwargs))
            except StopIteration:
                continue
            logger.debug(f"value:{value}")
            d[key] = value 
        d["jsn"] = kwargs
        logger.debug(d)
        super(DirectMessageManager, self).create(**d)       
        """
        self.objects.create(self.id = d["id"],
                            self.created_timestamp = d["created_timestamp"],
                            self.sender_id = d["sender_id"],
                            self.recipient_id = d["recipient_id"],
                            self.source_app_id = d["source_app_id"],
                            self.text = d["text"],
                            self.json = jsn)
        """

class DirectMessage(models.Model):
    id = models.BigIntegerField(unique=True, primary_key=True)
    created_timestamp = models.BigIntegerField(help_text=_('Milliseconds since epoch') )
    sender_id = models.BigIntegerField()
    recipient_id = models.BigIntegerField()
    source_app_id = models.BigIntegerField(null=True)
    text = models.TextField()
    jsn = JSONField()
    
    objects = DirectMessageManager()
    
    class Meta:
        ordering = ['-created_timestamp']
        get_latest_by = "-created_timestamp"
    
    def __str__(self):
        if getConfig()["settings"]["bot_id"] == self.sender_id:
            direction = "Sent"
        else:
            direction = "Received"
            
        return "{direction}: '{text}'".format(direction=direction, text=self.text[:140])