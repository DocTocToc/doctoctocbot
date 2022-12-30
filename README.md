# DocTocTocBot

tldr; Twitter retweet bot, Mastodon reblog bot supporting multiple hashtags and communities with automated collective user vetting / moderation through Direct Messages. Advanced community tools (website, crowdfunding app, keyword filter, search engine, tagging, etc.).

This project started as a simple Twitter retweet bot to enhance the hashtag #doctoctoc
("Toc, toc!" is the equivalent of "Knock, knock!" in French, but is not used to
introduce a joke).
\#DocTocToc is used by French speaking doctors, midwives and other healthcare
professionals to help each other by asking questions about clinical cases or
administrative chores.

This software is now used by other international healthcare communities such as
the #askrenalpath community composed of renal pathologists.

We support multiple communities run by different Mastodon / Twitter accounts. Each account can track and retweet / reblog a different set of hashtags.
Each community has a dedicated web site which is made of automatic content and
specific human contributed blocks of text.

Each web site allows to browse the archive of tweets by date, category and tag and to search all recorded tweets.

Access to data and metadata API is fully controlled by an authorization matrix.

This project includes a unique collective moderation system using a Twitter DM feature called "QuickReply". Members of your community can become moderators and decide which Twitter users will be retweeted by simply pushing a button to reply to a DM sent by the bot!

Retweeting of specific tweets can be prevented by keyword analysis of their
text. Complex boolean logic is supported.

Contributions are welcome. Data mining, NLP hackers, we need you!

## Cloning this repository
This repository contains a submodule ```src/bot/lib/python-twitter```. It is a modified version of python-twitter that allows sending and retrieving direct messages with the new Twitter API.

For a 1st time clone use

```
git clone --recursive https://github.com/DocTocToc/doctoctocbot.git
```

If you already cloned the repository, cd into it and

```
git submodule update --init --recursive
```

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

@DocTocTocBot was created on 07/03/2017 by Jerome Pinguet [@MedecineLibre](https://twitter.com/medecinelibre)


## Mastodon
Since December 2022, [Mastodon](https://mastodon.social) bots are available.

## Languages

Backend runs on Django, Python. Tasks run on Celery.

Frontend uses a mix of Django HTML templates, JavaScript and Svelte components.

![alt text](https://img.shields.io/badge/python-3.10-green.svg "Python3.10")

Python & Django version
--------------
* Python version 3.10
* Django version 3.2

How to start:
-------------

Our Mastodon reblog bot and our Twitter retweet bot are integrated into a larger Django project adapted to power and moderate a large Twitter and/or Mastodon community. This code is currently used to support a community of 9343 healthcare professionals moderated by 27 people.

Code can run on any system supporting Docker and Docker Compose.

Our production server manages around 9000 Twitter followers from 7 communities on a Digital Ocean droplet (8 GB Memory / 4 AMD vCPUs / 160 GB Disk / Ubuntu 20.04 (LTS) x64
).

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
* Contact the main developer Jérome Pinguet on Mastodon [@medecinelibre@mastodon.medica.im](https://mastodon.medica.im/@medecinelibre) or [@MedecineLibre](https://twitter.com/MedecineLibre)
* Use our GnuPG encrypted [contact form](https://doctoctoc.net/contact)