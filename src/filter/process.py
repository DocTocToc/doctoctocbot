import logging
import re
import unidecode
import string
from typing import Set
from filter.models import Filter
from community.models import Community
from conversation.models import Tweetdj

logger = logging.getLogger(__name__)

def add_attributes(obj, d):
    # iterate dictionary and add attributes
    for name, value in d.items():
        setattr(obj, name, set(value))

def add_self(string, sub):
    to_add = "self."
    indexes = [m.start() for m in re.finditer(sub, string)]
    for idx, index in enumerate(indexes):
        i = index + idx*len(to_add)
        string = string[:i] + to_add + string[i:]
    return string


class Flag():
    def __init__(self, flagged=False, _filter=""):
        self.flagged = flagged
        self.filter = _filter
        
    def __repr__(self):
        return (
            'Flag (flagged: %s , filter: "%s")'  % (self.flagged, self.filter)
        )

    def __bool__(self):
        return self.flagged


class FilterStatus():
    def __init__(self, raw_status: str, community: str):
        self.raw_status = raw_status
        self.status = self.process_status()
        self.community = community
        
    def process_status(self):
        status = frozenset(
            unidecode.unidecode(
                "".join(
                    [
                        (ch if ch not in string.punctuation else " ")
                        for ch
                        in self.raw_status
                    ]
                )
            ).split()
        )
        return status

    def dictionary(self, filter):
        dct = {}
        for w in filter.word.all():
            dct[w.name]= w.word
        add_attributes(self, dct)
        
    def express(self, filter):
        e = filter.expression
        for w in filter.word.all():
            e = add_self(e, w.name)
        return add_self(e, "status")
    
    def filter(self) -> Flag:
        flag = Flag()
        try:
            community = Community.objects.get(name=self.community)
        except Community.DoesNotExist:
            return flag
        for f in Filter.objects.filter(community=community, active=True):
            self.dictionary(f)
            e = self.express(f)
            flagged = eval(e)
            if flagged:
                flag.flagged = True
                flag.filter = f.name
                return flag
        return flag

def filter_status(statusid: int, community: str):
    text = Tweetdj.getstatustext(statusid)
    if not text:
        return Flag()
    f = FilterStatus(raw_status=text, community=community)
    return f.filter()
            
            
            
    


