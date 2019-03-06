"""

Custom validators

"""
import unicodedata
import json
import logging

from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import six
from django.db import connection

from moderation.models import Profile

logger = logging.getLogger(__name__)

#where lower(data::text)::jsonb @> lower('[{"city":"New York"}]')::jsonb

RESERVED_NAME = _(u"This name is reserved and cannot be registered.")

def CaseInsensitiveReservedSocialUsername(value):
    """
    Validator which performs a case-insensitive uniqueness check.
    """
    # Only run if the username is a string.
    if not isinstance(value, six.text_type):
        return
    value = unicodedata.normalize('NFKC', value)
    if hasattr(value, 'casefold'):
        value = value.casefold()  # pragma: no cover
    #if self.model._default_manager.filter(**{
    #        '{}__iexact'.format(self.field_name): value
    #}).exists():
    with connection.cursor() as cursor:
        cursor.execute("""SELECT COUNT(*) FROM moderation_profile WHERE lower(json::text)::jsonb @> lower(%s)::jsonb""", [json.dumps({'screen_name': value})])
        row=cursor.fetchone()
    if row[0]:
        raise ValidationError(RESERVED_NAME, code='unique')

