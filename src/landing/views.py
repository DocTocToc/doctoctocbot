from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

def index(request):
    return render(request, 'landing/index.html')

class UserInfo(LoginRequiredMixin, TemplateView):
    template_name = 'landing/user.html'
    title = "User info"

    def get_context_data(self, *args, **kwargs):
        context = super(UserInfo, self).get_context_data(*args, **kwargs)
        uid = self.request.user.social_auth.get(provider='twitter').uid
        context['uid'] = uid
        return context
