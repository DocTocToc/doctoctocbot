import logging
from django.urls import reverse
from django.shortcuts import render
from django.views.generic import TemplateView
from django.conf import settings
from django.shortcuts import redirect
from django.utils.translation import gettext as _
from urllib.parse import urlparse, urlunparse

from bot.models import Account
from bot.tweepy_api import get_api

import tweepy

logger = logging.getLogger(__name__)

def is_twitter_auth(user):
    if not user.is_authenticated:
        return False
    return bool(user.social_auth.filter(provider='twitter'))

def verify_account_credentials(screen_name):
    api = get_api(username=screen_name, backend=True)
    try:
        return api.verify_credentials()
    except tweepy.TweepError:
        return False

class Request(TemplateView):
    title = _("Authorize our app")
    template_name = "authorize/request.html"

    def get_context_data(self, *args, **kwargs):
        context = super(Request, self).get_context_data(*args, **kwargs)
        user = self.request.user
        if is_twitter_auth(user):
            uid = user.social_auth.get(provider="twitter").uid
            try:
                account = Account.objects.get(userid=uid)
            except Account.DoesNotExist:
                account = None
            if account:
                screen_name = user.social_auth.get(provider="twitter").extra_data["access_token"]["screen_name"]
                if verify_account_credentials(screen_name):
                    context["redirect_url"] = None
                    context["error"] = False
                    context["verify_credentials"] = True
                    return context
            callback_url = self.request.build_absolute_uri(reverse('authorize:callback'))
            logger.debug(f"callback url: {callback_url}")
            parsed = urlparse(callback_url)
            callback_url_https = urlunparse(
                ['https' if i==0 else e for i,e in enumerate(parsed)]
            )
            logger.debug(f"callback url https: {callback_url_https}")
            try:
                auth = tweepy.OAuthHandler(
                    settings.TWITTER_APP_CONSUMER_KEY,
                    settings.TWITTER_APP_CONSUMER_SECRET,
                    callback_url
                )
            except tweepy.TweepError:
                logger.debug("auth error")
            try:
                redirect_url = auth.get_authorization_url()
                context["redirect_url"] = redirect_url
                self.request.session['request_token'] = auth.request_token['oauth_token']
            except tweepy.TweepError:
                print('Error! Failed to get request token.')
                context["redirect_url"] = None
                context["error"] = True
        return context


def Callback(request):
    user = request.user
    if is_twitter_auth(user):
        verifier = request.GET.get('oauth_verifier')
        logger.debug(f"verifier: {verifier}")
        auth = tweepy.OAuthHandler(
            settings.TWITTER_APP_CONSUMER_KEY,
            settings.TWITTER_APP_CONSUMER_SECRET,
        )
        token = request.session.get('request_token')
        logger.debug(f"token: {token}")
        request.session.delete('request_token')
        auth.request_token = { 'oauth_token' : token,
                             'oauth_token_secret' : verifier }
        uid = user.social_auth.get(provider="twitter").uid
        screen_name = user.social_auth.get(provider="twitter").extra_data["access_token"]["screen_name"]
        try:
            account = Account.objects.get(userid=uid)
        except Account.DoesNotExist:
            account = Account.objects.create(
                username=screen_name,
                userid=uid
            )
        verify_credentials = verify_account_credentials(screen_name)
        if verify_credentials:
            return redirect(reverse("authorize:success"))
        try:
            auth.get_access_token(verifier)
        except tweepy.TweepError:
            logger.error('Failed to get access token.')
            return redirect(reverse("authorize:error"))
        consumer_key = settings.TWITTER_APP_CONSUMER_KEY
        consumer_secret = settings.TWITTER_APP_CONSUMER_SECRET,
        account.twitter_consumer_key = consumer_key
        account.twitter_consumer_secret =  consumer_secret
        account.twitter_access_token = auth.access_token
        account.twitter_access_token_secret = auth.access_token_secret
        account.backend_twitter_consumer_key = consumer_key
        account.bachend_twitter_consumer_secret = consumer_secret
        account.bachend_twitter_access_token = auth.access_token
        account.bachend_twitter_access_token_secret = auth.access_token_secret
        account.save()
        return redirect(reverse("authorize:success"))
    else:
        return redirect(reverse("authorize:request"))


            
        
    