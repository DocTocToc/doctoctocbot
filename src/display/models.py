import time
from django.db import models
from conversation.tree.tweet_parser import Tweet 

# Create your models here.

class WebTweet(models.Model):
    statusid = models.BigIntegerField(unique=True, primary_key=True)
    conversationid = models.BigIntegerField()
    userid = models.BigIntegerField()
    username = models.CharField(max_length=15)
    name = models.CharField(max_length=50)
    time = models.PositiveIntegerField(help_text="time in seconds since epoch")
    html = models.TextField()
    text = models.TextField()
    reply = models.PositiveIntegerField(null=True)
    like = models.PositiveIntegerField(null=True)
    retweet = models.PositiveIntegerField(null=True)
    parentid = models.BigIntegerField(null=True)
    rtl = models.BooleanField(help_text="right to left")
    image0 = models.CharField(max_length=200, null=True)
    image1 = models.CharField(max_length=200, null=True)
    image2 = models.CharField(max_length=200, null=True)
    image3 = models.CharField(max_length=200, null=True) 
    avatar_mini = models.CharField(max_length=200)
    avatar_normal = models.CharField(max_length=200)
    avatar_bigger = models.CharField(max_length=200)
    
    def localtime(self):
        """
        Converts the epoch in seconds from a Tweet object to a Python localtime object
        """
        return time.localtime(self.time)
    
    def utctime(self):
        return time.gmtime(self.time)
    
def createwebtweet(tweet: Tweet):
    
    images = {}
    for i in range(4):
        key: str = "image" + str(i)
        images[key]= None
        
    for idx, url in enumerate(tweet.images):
            key = "image"+ str(idx)
            images[key] = url
        
    WebTweet.objects.create(statusid=tweet.statusid,
                            conversationid=tweet.conversationid,
                            userid=tweet.userid,
                            username=tweet.username,
                            name=tweet.name,
                            time=tweet.time,
                            html=tweet.bodyhtml,
                            text=tweet.bodytext,
                            reply=tweet.replies,
                            like=tweet.favorites,
                            retweet=tweet.retweets,
                            rtl=tweet.rtl,
                            image0= images['image0'],
                            image1= images['image1'],
                            image2= images['image2'],
                            image3= images['image3'],
                            avatar_mini=tweet.avatar_mini,
                            avatar_normal=tweet.avatar_normal,
                            avatar_bigger=tweet.avatar_bigger)