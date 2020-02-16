import logging

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from invite.forms import InviteForm
from django.http import HttpResponseRedirect
from discourse.templatetags.auth_discourse import is_allowed_discussion
from invitations.utils import get_invitation_model
from moderation.models import Category

logger = logging.getLogger(__name__)

@login_required
def invite(request):
    # if this is a POST request we need to process the form data    
    if request.method == 'POST':

        # create a form instance and populate it with data from the request:
        form = InviteForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            logger.debug(form.cleaned_data)
            #send_invitation(form)
            # redirect to a new URL:
            category_name = form.cleaned_data['category']
            try:
                category = Category.objects.get(name=category_name)
            except Category.DoesNotExist:
                return HttpResponseRedirect('/thanks/')
            Invitation = get_invitation_model()
            invite = Invitation.create(
                form.cleaned_data['email'],
                category=category,
                inviter=request.user
            )
            invite.send_invitation(request)
            return HttpResponseRedirect('/thanks/')

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