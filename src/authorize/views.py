import logging
from django.urls import reverse
from django.shortcuts import render
from django.views.generic import TemplateView
from django.conf import settings
from django.shortcuts import redirect
from django.utils.translation import gettext as _
from urllib.parse import urlparse, urlunparse

import tweepy

logger = logging.getLogger(__name__)

def is_twitter_auth(user):
    if not user.is_authenticated:
        return False
    return bool(user.social_auth.filter(provider='twitter'))


class Request(TemplateView):
    title = _("Authorize our app")
    template_name = "authorize/request.html"

    def get_context_data(self, *args, **kwargs):
        context = super(Request, self).get_context_data(*args, **kwargs)
        user = self.request.user
        if is_twitter_auth(user):
            callback_url = self.request.build_absolute_uri(reverse('authorize:callback'))
            logger.debug(f"callback url: {callback_url}")
            t = urlparse(callback_url)
            if t.scheme == "http":
                t.scheme = "https"
            callback_url = urlunparse(t)
            logger.debug(f"callback url: {callback_url}")
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
            except tweepy.TweepError:
                print('Error! Failed to get request token.')
                context["redirect_url"] = None
                context["error"] = True
        return context


def Callback(request):
    return redirect(reverse("authorize:success"))

            
        
    