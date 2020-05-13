from django.urls import reverse
from django.shortcuts import render
from django.views.generic import TemplateView
from django.conf import settings
from django.shortcuts import redirect
from django.utils.translation import gettext as _

import tweepy

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
            auth = tweepy.OAuthHandler(
                settings.TWITTER_APP_CONSUMER_KEY,
                settings.TWITTER_APP_CONSUMER_SECRET,
                self.request.build_absolute_uri(reverse('authorize:callback'))
            )
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

            
        
    