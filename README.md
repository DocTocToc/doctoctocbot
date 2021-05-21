# DocTocTocBot

This project started as a Twitter retweet bot to enhance the hashtag #doctoctoc
("Toc, toc!" is the equivalent of "Knock, knock!" in French, but is not used to
introduce a joke).
\#DocTocToc is used by French speaking doctors, midwives and other healthcare
professionals to help each other by asking questions about clinical cases or
administrative chores.

This software is now used by other international healthcare communities such as
the #askrenalpath community composed of renal pathologists.

We support multiple communities run by different Twitter accounts. Each account
can track and retweet a different set of hashtags.
Each community has a dedicated web site which is made of automatic content and
specific human contributed blocks of text.

Each web site allows to browse the archive of tweets by date, category and tag.

Access to data and metadata API is fully controlled by an authorization matrix.

This project includes a unique collective moderation system using a Twitter DM feature called "QuickReply". Members of your community can become moderators and decide which Twitter users will be retweeted by simply pushing a button to reply to a DM sent by the bot!

Retweeting of specific tweets can be prevented by keyword analysis of their
text. Complex boolean logic is supported.

Contributions are welcome. Data mining, NLP hackers, we need you!

## Cloning this repository
This repository contains a submodule ```src/bot/lib/python-twitter```. It is a modified version of python-twitter that allows sending and retrieving direct messages with the new Twitter API.

For a 1st time clone use

```git clone --recursive https://github.com/DocTocToc/doctoctocbot.git```

If you already cloned the repository, cd into it and

```git submodule update --init --recursive```

## Retweet rules

Code can easily be adapted to suit your own set of rules.

These are the rules currently applied to our main account:

1. I retweet tweets containing the hashtag #doctoctoc
2. I retweet only MDs and midwives
3. I retweet only my followers
4. I don't retweet retweets
5. I don't retweet answers
6. I don't retweet "quote tweets"
7. I exclude a few usecases such as professionals looking for a replacement
8. I retweet only questions

[Full set of rules](https://doctoctoc.net/rules)(French)



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

Our Twitter retweet bot is integrated into a larger Django project adapted to power and moderate a large Twitter community. This code is currently used to support a community of 900 healthcare professionals moderated by 15 persons.

Tips for running this code on a Debian based GNU/Linux server: [Installation on Debian & Ubuntu](https://github.com/DocTocToc/doctoctocbot/wiki/Installation-on-Debian-&-Ubuntu)

* Define the hashtag(s) you want to retweet and the hashtag(s) you want to track and store in the Django admin (Hashtag model, conversation app).
* You can track more hashtags than you retweet (for archival purpose)
* Start the tracking stream: ```python3 manage.py run_bot_stream```
* You can also use the retweet bot based on Search API: ```python3 manage.py run_bot_search```
* You can run both Django commands with systemd.
* For the search and retweet module doctoctocbot.py, define the number of retweets at a time (This avoids overloading -Limit is 180 RT/ 15 mins)
* Add your Twitter app credentials in the admin (Account model, bot app)
* run celery (mandatory, the bot app launches celery tasks for retweets)
* optional: start the website (we use gunicorn)


## Crowdfunding
If you like this project and want to see it grow and improve, you can help by [investing money](https://doctoctoc.net/financement) in it.
This project includes its own crowdfunding app. The app lists funders who
accepted to go public. It produces real time statistics about the crowdfunding
campaign.
The Twitter bot of a community can thank participants anonymously or by
mentioning their Twitter handle. The bot can also send DMs inviting users to
donate according to a predefined set of rules.

## Thanks
To [@natolh](https://twitter.com/natolh) for his technical advice and pull requests.

## Contact
* [Start a private conversation with @doctoctocbot](https://twitter.com/messages/compose?recipient_id=881706502939185152)
* Contact the main developer @medecinelibre on [Mastodon](https://mastodon.xyz/web/accounts/7594) or [Twitter](https://twitter.com/MedecineLibre)
* Use our GnuPG encrypted [contact form](https://doctoctoc.net/contact)
