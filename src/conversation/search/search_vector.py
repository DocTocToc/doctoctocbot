import logging
from conversation.models import (
    Tweetdj,
    PostgresqlDictionary,
    TwitterLanguageIdentifier,
)
from moderation.tasks import handle_socialuser_language
from conversation.tasks import handle_text_search_vector
from django.contrib.postgres.search import SearchVector
from django.db.models import Value
from moderation.models import addsocialuser
from whatthelang import WhatTheLang

logger = logging.getLogger(__name__)

class TextSearchVector():

    ok_lang = ["en", "fr"]
    all_entities = ["media", "urls", "user_mentions", "symbols", "hashtags"]
    entities = ["media", "urls", "user_mentions", "symbols"]
    wtl = WhatTheLang()
    try:
        simple_dict = PostgresqlDictionary.objects.get(cfgname="simple")
    except PostgresqlDictionary.DoesNotExist:
        simple_dict = None

    def __init__(self, tweetdj: Tweetdj, config: str | None = None):
        self.tweetdj = tweetdj
        self.config = config
        self.text = self.get_text()
        self.dictionary: PostgresqlDictionary | None = None

    def get_text(self):
        try:
            return self.tweetdj.json["full_text"]
        except TypeError:
            return
        except KeyError:
            try:
                return self.tweetdj.json["text"]
            except KeyError:
                logger.error(
                    f"status {self.tweetdj.statusid}:\n"
                    "json field contains neither 'full_text' nor 'text' key"
                )
                
    def is_entity_only(self):
        count = 0
        for entity_key in TextSearchVector.all_entities:
            try:
                entity_lst = self.tweetdj.json["entities"][entity_key]
            except KeyError:
                continue
            count += len(entity_lst)
        return len(self.get_text().split()) == count

    def expunge_entities(self):
        # get list of indices tuples
        indices: list(tuple) = []
        for entity_key in TextSearchVector.entities:
            try:
                entity_lst = self.tweetdj.json["entities"][entity_key]
            except KeyError:
                continue
            for entity in entity_lst:
                indices.append(tuple(entity["indices"]))
        if not indices:
            return
        indices.sort(key=lambda x: x[0])
        new = ""
        txt = self.text
        for i,j in indices:
            new += txt[:i]
            new += " "*(j-i)
            new += txt[j:]
            txt=new
            new=""
        self.text=txt

    def remove_hash(self):
        # remove hash from hashtags
        indices: list(tuple) = []
        try:
            entity_lst = self.tweetdj.json["entities"]["hashtags"]
        except KeyError:
            return
        for entity in entity_lst:
            indices.append(tuple(entity["indices"]))
        if not indices:
            return
        indices.sort(key=lambda x: x[0])
        new = ""
        txt = self.text
        for i, _ in indices:
            new += txt[:i]
            new += " "
            new += txt[i+1:]
            txt=new
            new=""
        self.text=txt

    def remove_invalid_screen_name(self):
        """ Remove words starting with '@' corresponding to defunct
        screen_names """
        self.text=' '.join(
            [word for word in self.text.split() if word[0] != "@"]    
        )

    def get_lang_socialuser(self):
        try:
            return self.tweetdj.socialuser.language.tag
        except AttributeError:
            addsocialuser(self.tweetdj)
            self.tweetdj.refresh_from_db()
            try:
                return self.tweetdj.socialuser.language.tag
            except AttributeError:
                handle_socialuser_language(self.tweetdj.socialuser.id)
                su = self.tweetdj.socialuser
                su.refresh_from_db()
                try:
                    return su.language.tag
                except:
                    return

    def get_lang(self):
        try:
            tag = self.tweetdj.json["lang"]
            logger.debug(f'\ntwitter {tag=}')
        except (TypeError, KeyError) as e:
            logger.debug(f'{self.tweetdj}: {e}')
            return
        if tag in TextSearchVector.ok_lang:
            return tag
        try:
            tag = TextSearchVector.wtl.predict_lang(self.text)
        except ValueError as e:
            logger.error(e)
            tag = None
        logger.debug(f'\nwtl{tag=}')
        if tag in TextSearchVector.ok_lang:
            return tag
        tag = self.get_lang_socialuser()
        logger.debug(f'\nsocialuser {tag=}')
        if tag in TextSearchVector.ok_lang:
            return tag

    def get_dictionary(self, tag):
        try:
            dict = (
                TwitterLanguageIdentifier.objects.get(tag=tag)
                .postgresql_dictionary
            )
        except TwitterLanguageIdentifier.DoesNotExist as e:
            logger.error(f'{self.tweetdj}: {tag=} {e}')
            dict = None
        return dict or TextSearchVector.simple_dict

    def update_status_text(self):
        if not self.tweetdj.json:
            logger.debug("\njson is None")
            return
        if self.is_entity_only():
            logger.debug("\nonly entities")
            return
        self.expunge_entities()
        self.remove_hash()
        self.remove_invalid_screen_name()
        if not self.text:
            logger.debug("\nno text lef")
            return
        if not self.config:
            tag = self.get_lang()
            if tag:
                self.dictionary = self.get_dictionary(tag)
            else:
                logger.debug("no allowed lang tag found: skip")
                return
            self.config = self.dictionary.cfgname
        sv=SearchVector(
            Value(self.text),
            config=self.config
        )
        self.tweetdj.status_text=sv
        self.tweetdj.save()