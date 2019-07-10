from bs4 import BeautifulSoup
from contextlib import closing
from requests import get, RequestException
import logging
logger = logging.getLogger(__name__)

def raw_html(url: str) -> bytes:
    """
    Return raw html source of given url.
    """
    def is_good_response(resp):
        content_type = resp.headers['Content-Type'].lower()
        return(resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)
    
    def log_error(e):
        print(e)
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.5"}
    try:
        with closing(get(url, headers=headers, timeout=3, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None
    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None
    
def doc_from_raw_html(raw_html: bytes) -> BeautifulSoup:
    soup = BeautifulSoup(raw_html, 'lxml', from_encoding="utf-8")
    return soup