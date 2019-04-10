import logging
import time, random
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

def simple_get(url):
    """
    ...
    """
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.5"}
    tmin = 1.0
    tmax = 2.0
    time.sleep(random.uniform(tmin, tmax))
    try:
        with closing(get(url, headers=headers, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None
    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None

def is_good_response(resp):
    content_type = resp.headers['Content-Type'].lower()
    return(resp.status_code == 200
        and content_type is not None
        and content_type.find('html') > -1)

def log_error(e):
    logger(e)