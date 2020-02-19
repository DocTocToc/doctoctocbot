import logging
from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils import translation
from invite.forms import InviteForm
from django.http import HttpResponseRedirect
from discourse.templatetags.auth_discourse import is_allowed_discussion
from invitations.utils import get_invitation_model
from invitations.views import SendInvite
from moderation.models import Category
from django.utils.translation import ugettext_lazy as _


logger = logging.getLogger(__name__)

"""
@login_required
def invite(request):
    user_language = settings.LANGUAGE_CODE
    translation.activate(user_language)
    request.session[translation.LANGUAGE_SESSION_KEY] = user_language
    # if this is a POST request we need to process the form data    
    if request.method == 'POST':

        # create a form instance and populate it with data from the request:
        form = InviteForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            if not is_allowed_discussion(request.user):
                return HttpResponseRedirect('/invite/thanks/')
            # process the data in form.cleaned_data as required
            logger.debug(form.cleaned_data)
            #send_invitation(form)
            # redirect to a new URL:
            category_name = form.cleaned_data['category']
            try:
                category = Category.objects.get(name=category_name)
            except Category.DoesNotExist:
                return HttpResponseRedirect('/invite/thanks/')
            Invitation = get_invitation_model()
            invite = Invitation.create(
                form.cleaned_data['email'],
                category=category,
                inviter=request.user
            )
            invite.send_invitation(request)
            return HttpResponseRedirect('/invite/thanks/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = InviteForm()

    return render(
        request,
        'invite/invite.html',
        {
            'allowed': is_allowed_discussion(request.user),
            'form': form
        }
    )
"""
    
class SendCategoryInvite(SendInvite):
    template_name = 'invite/invite.html'
    form_class = InviteForm


    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(SendCategoryInvite, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SendCategoryInvite, self).get_context_data(**kwargs)
        context['allowed'] = is_allowed_discussion(self.request.user)
        return context

    def form_valid(self, form):
        if not is_allowed_discussion(self.request.user):
            return self.form_invalid(form)
        email = form.cleaned_data["email"]
        category_name = form.cleaned_data['category']
        try:
            category = Category.objects.get(name=category_name)
        except Category.DoesNotExist:
            return self.form_invalid(form)
        try:
            invite = form.save(email, category)
            invite.inviter = self.request.user
            invite.save()
            invite.send_invitation(self.request)
        except Exception:
            return self.form_invalid(form)
        return self.render_to_response(
            self.get_context_data(
                success_message=_('%(email)s has been invited') % {
                    "email": email}))

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))