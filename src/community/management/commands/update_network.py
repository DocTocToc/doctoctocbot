import itertools
import logging
import time
import pytz
from datetime import datetime, timedelta
from django.core.management.base import  BaseCommand, CommandError
from community.prospect import Prospect
from moderation.models import (
    SocialUser,
    Category,
    Friend,
    Follower,
    SocialMedia
)
from community.models import Community
from bot.models import Account
from bot.tweepy_api import get_api
from moderation.social import update_social_ids

logger = logging.getLogger(__name__)


class FastProspect(Prospect):
    def update_network(self, api_lst, sleep, cache_delta):
        twitter=SocialMedia.objects.get(name='twitter')
        datetime_limit = datetime.now(pytz.utc) - cache_delta
        logger.debug(f'\n{datetime_limit=}\n')
        api_generator = itertools.cycle(api_lst)
        for i in range(0, len(self.members_user_id), 100):
            api = next(api_generator)
            user_ids=self.members_user_id[i:i+100]
            users=api.lookup_users(user_ids)
            not_protected = [
                user.id for user in users if not user._json["protected"]
            ]
            for user_id in not_protected:
                try:
                    su=SocialUser.objects.get(
                        user_id=user_id,
                        social_media=twitter
                    )
                except SocialUser.DoesNotExist:
                    continue
                logger.info(f'{self.known_network()}')
                for relationship in ['friends', 'followers']:
                    if relationship=='friends':
                        if Friend.objects.filter(
                            user=su, created__gte=datetime_limit
                        ).exists():
                            continue
                    if relationship=='followers':
                        if Follower.objects.filter(
                            user=su, created__gte=datetime_limit
                        ).exists():
                            continue
                    update_social_ids(
                        su,
                        cached=False,
                        relationship=relationship,
                        api=next(api_generator),
                        delta=cache_delta
                    )
                    if sleep:
                        time.sleep(sleep)


class Command(BaseCommand):
    help = 'Prospect new members for a community'
    def add_arguments(self, parser):
        parser.add_argument(
            'community',
            type=str,
            help='Community to prospect for')
        parser.add_argument(
            '--category',
            type=str,
            help='Which category of users are we looking for?'
        )
        parser.add_argument(
            '--cache',
            type=int,
            help='Update relationship data if more than cache days old'  
        )

    def handle(self, *args, **options):
        community_name = options["community"]
        category_name = options["category"]
        cache = options["cache"] or 7

        try:
            community = Community.objects.get(name=community_name)
        except Community.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(
                    f"'{community_name}' does not exist."
                )
            )
            return
        try:
            category = Category.objects.get(name=category_name)
        except Category.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(
                    f"'{category_name}' does not exist."
                )
            )
            return

        p = FastProspect(
            community=community,
            category=category,
            network_cache = cache,
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'{p.known_network()}'
            )
        )
        api_lst=[]
        for account in Account.objects.filter(active=True):
            api = get_api(account.username)
            verify = api.verify_credentials()
            if verify:
                logger.debug(str(verify)[:100])
                api_lst.append(api)
        logger.debug(f'\n{len(api_lst)=}\n')
        sleep=60/len(api_lst)
        cache_delta = timedelta(days=cache)
        p.update_network(api_lst=api_lst, sleep=sleep, cache_delta=cache_delta)
        self.stdout.write(
            self.style.SUCCESS(
                f'{p.known_network()}'
            )
        )