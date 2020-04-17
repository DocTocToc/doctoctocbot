from django.test import TestCase
import random
import string
import datetime
from conversation.models import Tweetdj
from bot.bin.thread import tweetdj_has_q_m

def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for _i in range(stringLength))

class tweetdj_has_q_mTest(TestCase):
    json = {
        "full_text": None,
    }
    json["full_text"] = randomString()

    def create_tweetdj(
            self,
            statusid=random.getrandbits(63),
            userid=random.getrandbits(63),
            json=json,
    ):
        return Tweetdj.objects.create(
            statusid=statusid,
            userid=userid,
            json=json,
            created_at=datetime.datetime.now(tz=datetime.timezone.utc),
        )
        
    def test_tweetdj_has_q_m_true(self):
        json = self.json
        json["full_text"] = json["full_text"] + "?"
        tweetdj = self.create_tweetdj(json=json)
        self.assertEqual(tweetdj_has_q_m(tweetdj), True)

    def test_tweetdj_has_q_m_false(self):
        tweetdj = self.create_tweetdj(json=self.json)
        self.assertEqual(tweetdj_has_q_m(tweetdj), False)