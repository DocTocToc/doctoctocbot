# DocTocTocBot

A Twitter bot to enhance the hashtag #doctoctoc ("Toc, toc!" is the equivalent of "Knock, knock!" in French, but is not used to introduce a joke).
\#DocTocToc is used by French speaking doctors, midwives and other healthcare professionals to help each other with clinical cases or administrative chores.

This project includes a unique collective moderation system using a Twitter DM feature called "QuickReply". Members of your community can become moderators and decide which Twitter users will be retweeted by simply pushing a button to reply to a DM sent by the bot!

Contributions are welcome. Data mining, NLP hackers, I need you!

## Cloning this repository
This repository contains a submodule ```src/bot/lib/python-twitter```. It is a modified version of python-twitter that allows sending and retrieving direct messages with the new Twitter API.

For a 1st time clone use

```git clone --recursive https://github.com/DocTocToc/doctoctocbot.git```

If you already cloned the repository, cd into it and

```git submodule update --init --recursive```

## DocTocTocBot rules

1. I retweet tweets containing the hashtag #doctoctoc
2. I retweet only MDs and midwives
3. I retweet only my followers
4. I don't retweet retweets
5. I don't retweet answers
6. I don't retweet "quote tweets"
7. I exclude a few usecases such as professionals looking for a replacement
8. I retweet only questions

[Full set of rules](https://doctoctoc.net/rules)(French)

## Challenges

* How to tell MDs from non-MDs on Twitter?
* How to enhance the dialogue with other healthcare professionals (pharmacists, ...)?
* Can we automatically classify the type of request (clinical case, administrative tip, other kind of help)?
* Can we automatically classify the medical category of the request? (Dermatology, cardiology, psychiatry, social problems)
* What classifications should we use? (ICPC, ICD)
* Should we use another hashtag for clinical quizzes (when the requester already knows the answer) such as \#DocQuiz ?

## Wiki, documentation, links

Read more about technical issues, code: [wiki](https://github.com/jeromecc/doctoctocbot/wiki)

[Présentation du robot en français](https://freemedsoft.com/fr/bot/doctoctoc/)

@DocTocTocBot was created on 07/03/2017 by [@medecinelibre](https://twitter.com/medecinelibre)


## Future
We would like to adapt the bot to [Mastodon](https://mastodon.social). Can you
help with this?

![alt text](https://img.shields.io/badge/python-3.7-green.svg "Python3.7")

Python & Django version
--------------
* Python version 3.7
* Django version 2.2

Dependencies:
-------------
See requirements folder.

```
pip install -r requirements/common.txt
pip install -r requirements/staging.txt
pip install -r requirements/development.txt
```


How to start:
-------------

Our Twitter retweet bot is now integrated into a larger Django project. Still, the bot app inside ```src/bot``` could be adapted as a standalone retweet bot.

Tips for running this code on a Debian based GNU/Linux server: [Installation on Debian & Ubuntu](https://github.com/DocTocToc/doctoctocbot/wiki/Installation-on-Debian-&-Ubuntu)

* Define the hashtag(s) you want to retweet and the hashtag(s) you want to track in the Django settings.py file.
* You can track more hashtags than you retweet (for archival purpose)
* Start the tracking stream: ```python3 manage.py run_bot_stream```
* You can also use the retweet bot based on Search API: ```python3 manage.py run_bot_search```
* You can run both Django commands with systemd.
* For the search and retweet module doctoctocbot.py, define the number of retweets at a time (This avoids overloading -Limit is 180 RT/ 15 mins)
* Add your Twitter app credentials in the settings.py file
* (Tune some other options if you like)

## Crowdfunding


## Thanks
To [@natolh](https://twitter.com/natolh) for his technical advice and pull requests.

## Contact
* [Start a private converstion with @doctoctocbot](https://twitter.com/messages/compose?recipient_id=881706502939185152)
* [Contact @medecinelibre on Mastodon](https://mastodon.xyz/web/accounts/7594)
