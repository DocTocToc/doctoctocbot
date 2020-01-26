import logging
import base64
import hmac
import hashlib
from urllib import parse

from django.contrib.auth.decorators import login_required
from django.http import (HttpResponseBadRequest, HttpResponseRedirect,
                         HttpResponse, HttpResponseForbidden)
from django.conf import settings
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from discourse.templatetags.auth_discourse import is_allowed_discussion
from ip.views import ip_yours
from ip.host import hostname_ip
from django.core.cache import cache
from ip.host import set_discourse_ip_cache

logger = logging.getLogger(__name__)

@login_required
def discourse_sso(request):
    '''
    Code adapted from https://meta.discourse.org/t/sso-example-for-django/14258
    '''
    payload = request.GET.get('sso', None)
    signature = request.GET.get('sig', None)

    if None in [payload, signature]:
        return HttpResponseBadRequest('No SSO payload or signature. Please contact support if this problem persists.')

    # Validate the payload

    payload = bytes(parse.unquote(payload), encoding='utf-8')
    decoded = base64.decodebytes(payload).decode('utf-8')
    if len(payload) == 0 or 'nonce' not in decoded:
        return HttpResponseBadRequest('Invalid payload. Please contact support if this problem persists.')

    key = bytes(settings.DISCOURSE_SSO_SECRET, encoding='utf-8')  # must not be unicode
    h = hmac.new(key, payload, digestmod=hashlib.sha256)
    this_signature = h.hexdigest()

    if not hmac.compare_digest(this_signature, signature):
        return HttpResponseBadRequest('Invalid payload. Please contact support if this problem persists.')

    user = request.user
    if not is_allowed_discussion(user):
        return redirect("discourse:discourse-unauthorized")
    # Build the return payload
    qs = parse.parse_qs(decoded)

    params = {
        'nonce': qs['nonce'][0],
        'email': user.email,
        'external_id': user.id,
        'username': user.username,
        #'require_activation': 'true',
        'name': user.get_full_name(),
    }
    
    try:
        avatar_url = user.socialuser.profile.json["profile_image_url_https"]
    except AttributeError as e:
        logger.warn("Attribute error on user object", e)
    except KeyError as e:
        logger.warn("Key error on profile object json field", e)
    else:
        params["avatar_url"] = avatar_url

    return_payload = base64.encodebytes(bytes(parse.urlencode(params), 'utf-8'))
    h = hmac.new(key, return_payload, digestmod=hashlib.sha256)
    query_string = parse.urlencode({'sso': return_payload, 'sig': h.hexdigest()})

    # Redirect back to Discourse

    discourse_sso_url = 'https://{0}/session/sso_login?{1}'.format(settings.DISCOURSE_BASE_URL, query_string)
    logger.warning("discourse redirect url: %s", discourse_sso_url)
    return HttpResponseRedirect(discourse_sso_url)

@csrf_exempt
def webhook(request):
    discourse_ip = cache.get(settings.DISCOURSE_IP_CACHE_KEY)
    if not discourse_ip:
        discourse_ip = set_discourse_ip_cache()
    if ip_yours(request) is not discourse_ip:
        return HttpResponseForbidden('Permission denied.')
    else:
        return HttpResponse('pong')