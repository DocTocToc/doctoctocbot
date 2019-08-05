import logging
from doctocnet.celery import app
from urllib.parse import urlparse
from urllib.parse import urldefrag
from conversation.models import Tweetdj
from moderation.models import SocialUser
from link.models import Website, Link
from furl import furl
from django.db import IntegrityError, DatabaseError, transaction


logger = logging.getLogger(__name__)

@app.task
def normalize_link_all():
    for tweet_mi in Tweetdj.objects.filter(link=None):
        normalize_link(tweet_mi)

def normalize_link(tweet_mi):
    if tweet_mi.link_set.exists():
        return
    json = tweet_mi.json
    if "entities" in json.keys():
        entities = json["entities"]
        if "urls" in entities.keys():
            for url in [dict["expanded_url"] for dict in entities["urls"]]:
                f = furl(url)
                netloc = f.host
                link = "".join([f.host, str(f.path)])
                if len(link)>255:
                    link = f.host
                if not netloc or not link:
                        continue
                try:
                    with transaction.atomic():
                        website_mi, _ = Website.objects.get_or_create(network_location=netloc)
                except IntegrityError as e:
                    logger.error("Website %s already exists in database: %s" % (netloc, e))
                    continue
                except DatabaseError as e:
                    logger.error("database error %s", e)
                    continue
                try:
                    with transaction.atomic():
                        link_mi, _ = Link.objects.get_or_create(url=link, website=website_mi)
                except IntegrityError as e:
                    logger.error("Status: %s Screen_name: %s Link %s already exists in database: %s" % (json["id"], json["user"]["screen_name"],link, e))
                    continue
                except DatabaseError as e:
                    logger.error("database error %s", e)
                    continue
                # add m2m relationship to the status
                tweet_mi.link_set.add(link_mi)
                # add m2m relationship to the SocialUser
                try:
                    socialuser = SocialUser.objects.get(user_id=json["user"]["id"])
                except SocialUser.DoesNotExist:
                    continue
                link_mi.socialuser.add(socialuser)