from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
import json
import logging
import requests

from .forms import CustomerModelForm


logger = logging.getLogger(__name__)


def send_form(form):
    url = 'http://127.0.0.1:8008/customers/'
    r = requests.post(url, auth=('elkcloner', 'elkcloner'), json=form.cleaned_data)
    logger.debug(r)


@login_required
def get_customer(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = CustomerModelForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            logger.debug(form.cleaned_data)
            send_form(form)
            # redirect to a new URL:
            return HttpResponseRedirect('/thanks/')

    # if a GET (or any other method) we'll create a blank form
    else:
        data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email
        }
        form = CustomerModelForm(initial=data)

    return render(request, 'customer/customer.html', {'form': form})
