# doctoctocbot

A Twitter bot to enhance the hashtag #doctoctoc ("Toc, toc!" is the equivalent of "Knock, knock!" in French, but is not used to introduce a joke).
\#DocTocToc is used by French speaking doctors and other healthcare professionals to help each other with clinical cases or administrative chores.

Contributions to the code are welcome. Data mining, NLP hackers, I need you!

## DocTocTocBot rules

1. I retweet tweets containing the hashtag #doctoctoc.
2. I retweet only MDs and midwives.
3. Twitter users who do not want to be retweeted can DM me (manually processed please be patient) or block me (effective immediately).
4. I don't retweet retweets.
5. I don't retweet answers.
6. I don't retweet "quote tweets".
7. I exclude a few usecases such as professionals looking for a replacement.

## Challenges

* How to tell MDs from non-MDs on Twitter?
* How to enhance the dialogue with other healthcare professionals (pharmacists, midwives, ...)?
* Can we automatically classify the type of request (clinical case, administrative tip, other kind of help)?
* Can we automatically classify the medical category of the request? (Dermatology, cardiology, psychiatry, social problems)
* What classifications should we user? (ICPC, ICD)
* Should we use another hashtag for clinical quizzes (when the requester already knows the answer) such as \#DocQuiz ?

## Wiki, documentation, links

Read more about technical issues, code: [wiki](https://github.com/jeromecc/doctoctocbot/wiki)

[Présentation du robot en français](https://freemedsoft.com/fr/bot/doctoctoc/)

DocTocTocBot is maintained by [@medecinelibre](https://twitter.com/medecinelibre)


## Future
The bot will be adapted to [Mastodon](https://mastodon.social) soon.

![alt text](https://img.shields.io/badge/python-3.6-green.svg "Python3.6")

Python version
--------------
The bot and its accompanying modules are Written for Python3.6. You might make
them work with Python 2.7 but we are recommending neither not supporting this
version.

Dependencies:
-------------
* Tweepy
* SQLAlchemy
* configparser
* logging (if python_version < '3.0')
* unidecode

```pip install -r requirements.txt```

How to start:
-------------

* Define your the hashtag(s) you want to retweet and the hashtag(s) you want to trach in the config file.
* You can track more hashtags than you retweet (for archival purpose)
* Start the tracking stream: ```python3 stream.py```
* You can start up the steam automagically with systemd.
* For the search and retweet module doctoctocbot.py, define the number of retweets at a time (This avoids overloading -Limit is 180 RT/ 15 mins)
* Add your Twitter app credentials in the config file
* (Tune some other options if you like)
* Search and retweet ```python3 doctoctocbot.py```
* Add this call to your crontab(unix) (or something similar) to retweet all new tweets regularly

Compatibility
-------------

Compatible with Python 3.x ,tested on Python 3.6.

## Thanks
To [@natolh](https://twitter.com/natolh) for his technical advice and pull requests.
