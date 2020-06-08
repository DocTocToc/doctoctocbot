from constance import config
import logging

from autotweet.utils import send_post_request, sleep
from autotweet.login import AutoLogin

logger = logging.getLogger(__name__)

def accept_follower_requests(uids, auth_token):
    if not uids:
        return
    sleep()
    for uid in uids:
        accept_follower_request(uid, auth_token)
        sleep()
        
def accept_follower_request(uid, auth_token):
    if not uid:
        return
    response = send_post_request(
        auth_token=auth_token,
        url=f'https://mobile.twitter.com/follower_requests/{uid}/accept',
        commit="Accept",
        referer=config.follower_requests_url,
    )
    logger.info(f" response of {uid} POST: {response}")
        
def accept_follower(uid, account_username):
    autologin = AutoLogin(account_username)
    sleep()
    autologin.login_mobile_twitter()
    sleep()
    response = accept_follower_request(uid, autologin._authenticity_token)
    logger.info(f" response of {uid} POST: {response}")
    sleep()
    autologin.logout()
    