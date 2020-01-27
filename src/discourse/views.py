import logging
import base64
import hmac
import hashlib
import json
from urllib import parse
from django.utils.encoding import force_bytes
from django.contrib.auth.decorators import login_required
from django.http import (HttpResponseBadRequest,
                         HttpResponseRedirect,
                         HttpResponse,
                         HttpResponseForbidden,
                         HttpResponseServerError)
from django.conf import settings
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from discourse.templatetags.auth_discourse import is_allowed_discussion
from ip.views import ip_yours
from django.core.cache import cache
from ip.host import set_discourse_ip_cache
from django.views.decorators.http import require_POST
from discourse.user import user_created_pipe

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

@require_POST
@csrf_exempt
def webhook(request):
    logger.debug(request.META)
    
    # ip check
    discourse_ip = cache.get(settings.DISCOURSE_IP_CACHE_KEY)
    if not discourse_ip:
        discourse_ip = set_discourse_ip_cache()
    client_ip = ip_yours(request)
    logger.debug(f"client: {client_ip}, discourse: {discourse_ip}")
    if client_ip != discourse_ip:
        return HttpResponseForbidden('Permission denied.')

    # header signature check
    header_signature = request.META.get('HTTP_X_DISCOURSE_EVENT_SIGNATURE')
    logger.debug(f"header signature: {header_signature}")
    if header_signature is None:
        return HttpResponseForbidden('Permission denied.')
    sha_name, signature = header_signature.split('=')
    if sha_name != 'sha256':
        return HttpResponseServerError('Operation not supported.', status=501)
    mac = hmac.new(force_bytes(settings.DISCOURSE_WEBHOOK_SECRET), msg=force_bytes(request.body), digestmod=hashlib.sha256)
    if not hmac.compare_digest(force_bytes(mac.hexdigest()), force_bytes(signature)):
        return HttpResponseForbidden('Permission denied.')
    
    # If request reached this point we are in a good shape
    event_type = request.META.get('HTTP_X_DISCOURSE_EVENT_TYPE')
    event = request.META.get('HTTP_X_DISCOURSE_EVENT')
    if event_type == 'ping' and event == 'ping':
        return HttpResponse('pong')
    elif event_type == 'user':
        body = json.loads(request.body)
        logger.debug(f"body (json): {body}")
        if event == 'user_created':
            logger.debug("Discourse user created!")
            logger.debug(f"Request body: {request.body}")
            try:
                userid=body["user"]["id"]
                username=body["user"]["username"]
            except KeyError:
                return HttpResponseServerError('Internal server error.', status=500)
            user_created_pipe(userid=userid, username=username)            
        elif event == 'user_updated':
            logger.debug("Discourse user updated!")
            logger.debug(f"Request body: {request.body}")
        elif event == 'user_destroyed':
            logger.debug("Discourse user destroyed!")
        return HttpResponse('success')
    
    return HttpResponse(status=204)
        
    
    