import sys
import random
import datetime
from django.db.models import Max
from django.db.utils import DatabaseError
from moderation.models import SocialUser
from conversation.models import Hashtag
from faker import Faker
from conversation.fake.json import fake_json
from conversation.models import Tweetdj
from tagging.models import Category

fake = Faker()

# first, import a similar Provider or use the default one
from faker.providers import BaseProvider

# create new provider class. Note that the class name _must_ be ``Provider``.
class Provider(BaseProvider):
    def foo(self):
        return 'bar'


def get_random_socialuser():
    max_id = SocialUser.objects.all().aggregate(max_id=Max("id"))['max_id']
    while True:
        pk = random.randint(1, max_id)
        su = SocialUser.objects.filter(pk=pk).first()
        if su:
            return su    


class FakeTweetdj():
    def __init__(self):      
        self.statusid=FakeTweetdj._statusid()                 
        self.socialuser=get_random_socialuser()
        self.userid=self.socialuser.user_id
        self.hashtag_list =FakeTweetdj._random_hashtag_list()
        self.created_at=FakeTweetdj._random_datetime()
        self.json=fake_json(
            statusid=self.statusid,
            user_id=self.userid,
            user_screen_name=self.socialuser.screen_name_tag(),
            user_name=self.socialuser.name_tag(),
            hashtag_list=self.hashtag_list,
            created_at=self.created_at
        )
    
    @staticmethod
    def _statusid():
        return fake.pyint(min_value=1, max_value=sys.maxsize, step=1)
    
    @staticmethod
    def _random_hashtag_list():
        hashtag_count = Hashtag.objects.all().count()
        hashtag_list = list(Hashtag.objects.values_list('hashtag', flat=True))
        return fake.random_elements(
            hashtag_list,
            length= fake.random_int(min=1,max=hashtag_count),
            unique=True
        )
        
    @staticmethod
    def _random_datetime():
        dtnow = datetime.datetime.now(tz=datetime.timezone.utc)
        delta = datetime.timedelta(days=730)
        dt = fake.date_time_between_dates(
            datetime_start=dtnow-delta,
            datetime_end=dtnow,
            tzinfo=datetime.timezone.utc
        )
        return dt

    def create(self):
        try:
            tweetdj = Tweetdj.objects.create(
                statusid=self.statusid,
                userid=self.userid,
                socialuser=self.socialuser,
                json=self.json,
                created_at=self.created_at,
            )
        except DatabaseError:
            return
        for hashtag in self.hashtag_list:
            try:
                hashtag_instance = Hashtag.objects.get(hashtag=hashtag)
                tweetdj.hashtag.add(hashtag_instance)
            except:
                continue
        tag = fake.random_element(
            list(Category.objects.values_list('tag', flat=True))
        )
        tweetdj.tags.add(tag)


def create_random_tweetdj(n: int):
    for _ in range(n):
        t = FakeTweetdj()
        t.create()
            