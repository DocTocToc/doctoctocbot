from datetime import datetime

from django.test import TestCase

from conversation.models import Tweetdj
from conversation.utils import userhashtagcount
from conversation.utils import usertotalhashtagcount
from .constants import userhashtagcount0_data, userhashtagcount1_data
from .data import userhashtagcount_db



class Userhashtagcount0TestCase(TestCase):
    def setUp(self):
       userhashtagcount_db(userhashtagcount0_data)
       
    def test_userhashtagcount_0(self):
        userid = userhashtagcount0_data[0]["userid"]
        self.assertEqual(userhashtagcount(userid, 0), 1)
        
    def test_userhashtagcount_1(self):
        userid = userhashtagcount0_data[0]["userid"]
        self.assertEqual(userhashtagcount(userid, 1), 0)
        
class Userhashtagcount1TestCase(TestCase):
    def setUp(self):
       userhashtagcount_db(userhashtagcount1_data)
       
    def test_userhashtagcount_0(self):
        userid = userhashtagcount1_data[0]["userid"]
        self.assertEqual(userhashtagcount(userid, 0), 0)
        
    def test_userhashtagcount_1(self):
        userid = userhashtagcount1_data[0]["userid"]
        self.assertEqual(userhashtagcount(userid, 1), 1)