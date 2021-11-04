"""

Custom validators

"""
import unicodedata
import json
import logging

from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.db import connection

from moderation.models import Profile

logger = logging.getLogger(__name__)

#where lower(data::text)::jsonb @> lower('[{"city":"New York"}]')::jsonb

RESERVED_NAME = _(u"This name is reserved and cannot be registered.")
AT_SIGN = _(u"A username cannot contain the '@' character.")

def CaseInsensitiveReservedSocialUsername(value):
    """
    Validator which performs a case-insensitive uniqueness check.
    """
    # Only run if the username is a string.
    if not isinstance(value, str):
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


def no_at_sign(value):
    """
    Validator which disallows @.
    """
    # Only run if the username is a string.
    if not isinstance(value, str):
        return
    if "@" in value:
        raise ValidationError(AT_SIGN)
