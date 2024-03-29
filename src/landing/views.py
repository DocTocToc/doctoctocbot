import logging
import time
import json
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from django.views.generic import TemplateView
from django.conf import settings
from conversation.tree.tweet_server import get_tweet
from conversation.utils import userhashtagcount
from moderation.models import Profile
from customer.forms import CustomerModelForm, CustomerReadOnlyForm
from customer.models import Customer
from bootstrap_modal_forms.generic import BSModalUpdateView

logger = logging.getLogger(__name__)

def index(request):
    return render(request, 'landing/index.html')

def status(request, statusid):
    tweet = get_tweet(statusid)
    logger.debug(f"{tweet.localtime()}")
    localdatetime: str = time.strftime('%H:%M - %d %b %Y', tweet.localtime())
    utcdatetime: str = time.strftime('%d %B %Y %H:%M:%S', tweet.utctime())

    logger.debug(f"{localdatetime}")
    context = {'tweet': tweet,
               'bodyhtml': mark_safe(tweet.bodyhtml),
               'avatar_mini': mark_safe(tweet.avatar_mini),
               'localdatetime': localdatetime,
               'utcdatetime': utcdatetime}
    return render(request, 'landing/tweet.html', context)

class UserInfo(LoginRequiredMixin, TemplateView):
    template_name = 'landing/user.html'
    title = _("User")

    def get_context_data(self, *args, **kwargs):
        context = super(UserInfo, self).get_context_data(*args, **kwargs)
        
        if self.request.user.social_auth.exists():
            uid = self.request.user.social_auth.get(provider='twitter').uid
        else:
            uid = 0
        
        if self.request.user.socialuser is not None:
            _json = self.request.user.socialuser.profile.json
            if isinstance(_json, str):
                _json = json.loads(_json.replace("\'", "\""))
            userid= self.request.user.socialuser.user_id
            context['name'] = _json.get("name", None)
            context['screen_name'] = _json.get("screen_name", None)
            context['location'] = _json.get("location", None)
            context['hashtag'] = userhashtagcount(userid, self.request)    
            try:
                expanded_url = _json["entities"]["url"]["urls"][0]["expanded_url"]
            except KeyError:
                expanded_url = None
            context['expanded_url'] = expanded_url
        
            try:
                display_url = _json["entities"]["url"]["urls"][0]["display_url"]
            except KeyError:
                display_url = None        
            context['display_url'] = display_url
            context['uid'] = uid
        return context


class UserProfile(LoginRequiredMixin, TemplateView):
    template_name = 'landing/user/profile.html'
    title = _("Profile")

    def get_context_data(self, *args, **kwargs):
        context = super(UserProfile, self).get_context_data(*args, **kwargs)
        
        if self.request.user.social_auth.exists():
            uid = self.request.user.social_auth.get(provider='twitter').uid
        else:
            uid = 0
        
        if self.request.user.socialuser is not None:
            userid= self.request.user.socialuser.user_id
            context['hashtag'] = userhashtagcount(userid, self.request)  
            try:
                json = self.request.user.socialuser.profile.json
            except Profile.DoesNotExist:
                return context
            try:
                expanded_url = json["entities"]["url"]["urls"][0]["expanded_url"]
            except (KeyError, TypeError) as e:
                logger.error(e)
                expanded_url = None
            context['expanded_url'] = expanded_url
            try:
                display_url = json["entities"]["url"]["urls"][0]["display_url"]
            except (KeyError, TypeError) as e:
                logger.error(e)
                display_url = None        
            context['display_url'] = display_url
        return context


class CustomerUpdateView(BSModalUpdateView):
    model = Customer
    template_name = 'customer/update_customer.html'
    form_class = CustomerModelForm
    success_message = 'Success: billing data was updated.'
    success_url = reverse_lazy('landing:user-billing')


def CustomerReadOnlyFormView(request):
    form = CustomerReadOnlyForm(user=request.user)
    return render(request, 'landing/user/billing.html', {'form': form})
