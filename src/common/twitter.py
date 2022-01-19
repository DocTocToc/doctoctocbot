from .soup import raw_html, doc_from_raw_html
from django.conf import settings
import urllib.parse
from typing import List, Optional, Union

def get_url_for_screen_name(screen_name: str) -> str:
    if not screen_name:
        raise ValueError('screen_name is an empty string.')
    return f'https://twitter.com/{screen_name}'

def get_url_from_user_id(user_id: int) -> str:
    if not user_id:
        raise ValueError('user_id is empty.')
        return
    if not isinstance(user_id, int):
        raise TypeError('user_id is not an integer.')
        return
    return f"https://twitter.com/intent/user?user_id={user_id}"

def status_url_from_id(id: int) -> str:
    """ 
        Get tweet url given its status id.
      
        Due to changing behaviour of Twitter API the url pattern is stored in settings. 
      
        Parameters: 
        id (int): id of status 
      
        Returns: 
        str: status url 
      
    """
    return settings.TWITTER_STATUS_URL.format(id=id)     
        
def follower_count(screen_name: str) -> int:
    if not screen_name:
        raise ValueError('screen_name is an empty string.')
    raw = raw_html(get_url_for_screen_name(screen_name))
    if not raw:
        return
    soup = doc_from_raw_html(raw)
    return (
        soup
        .find_all(attrs={'data-nav':'followers'})[0]
        .find_all("span", class_="ProfileNav-value")[0]['data-count']
    )    

def search_string(
        words_any: Optional[List[str]] = None,
        words_all: Optional[List[str]] = None,
        exact_string: Optional[str] = None,
        from_account: Union[List[str], str, None] = None,
        to_account: Union[List[str], str, None] = None,
        excluded_words: Optional[List[str]] = None,
        min_replies: Optional[int] = None,
        min_faves: Optional[int]  = None,
        min_retweets: Optional[int] = None,
        ):
    def _words_any(words_any: Optional[List[str]]):
        if isinstance(words_any, str):
            return words_any
        query = " OR ".join(words_any)
        return "(" + query + ")"
    def _words_all(words_all: Optional[List[str]]):
        if isinstance(words_all, str):
            return words_all
        query = " ".join(words_all)
        return "(" + query + ")"
    def _from_account(from_account):
        if isinstance(from_account, str):
            return "from:" + from_account
        query = ["from:" + account for account in from_account]
        return "(" + " OR ".join(query) + ")"
    
    def _to_account(to_account):
        if isinstance(to_account, list):
            return "to:" + to_account
        query = ["to:" + account for account in to_account]
        return "(" + " OR ".join(query) + ")"

    base: str = "https://twitter.com/search?q="
    query = []
    if words_any:
        query.append(_words_any(words_any))
    if words_all:
        query.append(_words_all(words_all))
    if exact_string:
        query.append(exact_string)
    if from_account:
        query.append(_from_account(from_account))
    if to_account:
        query.append(_to_account(to_account))
    
    return base + urllib.parse.quote(" ".join(query))
    