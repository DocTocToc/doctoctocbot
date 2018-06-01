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


Dependecies:
-------------
* Tweepy

```pip install tweepy```

* Or alternatively

```pip install -r requirements.txt```

How to start:
-------------

* Define your hashtag or search query in the config file
* Define the number of Retweets at a time (This avoids overloading -Limit is 180 RT/ 15 mins)
* Add your Twitter app credentials in the config file
* (Tune some other options if you like)
* $ python retweet.py
* Add this call to your crontab(unix)/task scheduler(windows) (or something similar) to retweet all new tweets regularly

Compatibility
-------------

Compatible with Python 3.x ,tested on Python 3.6.

## Thanks
To [@natolh](https://twitter.com/natolh) for his technical advice and pull requests.
