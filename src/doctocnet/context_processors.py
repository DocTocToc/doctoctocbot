from django.contrib.sites.shortcuts import get_current_site
from django.utils.functional import SimpleLazyObject


def site(request):
    return {
        'site': SimpleLazyObject(lambda: get_current_site(request)),
    }