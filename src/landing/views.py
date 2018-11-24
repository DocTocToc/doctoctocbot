from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from conversation.utils import userhashtagcount
from bot.conf.cfg import getConfig

def index(request):
    return render(request, 'landing/index.html')

class UserInfo(LoginRequiredMixin, TemplateView):
    template_name = 'landing/user.html'
    title = "User info"

    def get_context_data(self, *args, **kwargs):
        context = super(UserInfo, self).get_context_data(*args, **kwargs)
        
        if self.request.user.social_auth.exists():
            uid = self.request.user.social_auth.get(provider='twitter').uid
        else:
            uid = None
        
        if self.request.user.socialuser is not None:
            json = self.request.user.socialuser.profile.json
            context['name'] = json.get("name", None)
            context['screen_name'] = json.get("screen_name", None)
            context['location'] = json.get("location", None)
        
            try:
                expanded_url = json["entities"]["url"]["urls"][0]["expanded_url"]
            except KeyError:
                expanded_url = None
            context['expanded_url'] = expanded_url
        
            try:
                display_url = json["entities"]["url"]["urls"][0]["display_url"]
            except KeyError:
                display_url = None        
            context['display_url'] = display_url
        
            context['uid'] = uid
            context['pp_url'] = json.get("profile_image_url_https", None)
            
            track_list = getConfig().get("keyword_track_list", None)
            context["hashtag0"] = None
            context["hashtag1"] = None
            if track_list is not None:
                for idx in range(len(track_list)):
                    context[f"hashtag{idx}"] = track_list[idx]
                  
        return context
