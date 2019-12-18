import logging

from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.utils.translation import gettext as _

from silver.models.billing_entities import Customer

logger = logging.getLogger(__name__)

def media_access(request, path):
    """
    When trying to access :
    myproject.com/media/uploads/passport.png

    If access is authorized, the request will be redirected to
    myproject.com/protected/media/uploads/passport.png

    This special URL will be handle by nginx we the help of X-Accel
    """

    access_granted = False

    user = request.user
    logger.debug(f"path:{path}")
    if user.is_authenticated:
        if user.is_staff:
            # If admin, everything is granted
            access_granted = True
        elif not path.startswith("documents/"):
            access_granted = True
        else:
            # For simple user, only their documents can be accessed
            try:
                customer = Customer.objects.get(customer_reference=str(user.id))
            except Customer.DoesNotExist:
                return HttpResponseForbidden(_('Not authorized to access this media.'))
            user_docs_path_lst = customer.billingdocumentbase_set.values_list('pdf__pdf_file', flat=True)
            logger.debug(f"user:{user}\n user_docs_path_lst:{user_docs_path_lst}")
            if path in user_docs_path_lst:
                access_granted = True

    if access_granted:
        response = HttpResponse()
        # Content-type will be detected by nginx
        del response['Content-Type']
        response['X-Accel-Redirect'] = '/protected/' + path
        return response
    else:
        return HttpResponseForbidden(_('Not authorized to access this media.'))