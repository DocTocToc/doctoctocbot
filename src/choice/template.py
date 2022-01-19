import logging
import markdown
from django.utils.safestring import mark_safe
from django.template import Template
from choice.models import Text

def choice_text(context, name):
    """ return text snippets
    
    available context:
      * diploma_slug
      * diploma_label
      * school_slug
      * school_tag
    """
    try:
        text = Text.objects.get(name=name)
    except Text.DoesNotExist:
        return
    return Template(text.content).render(context=context)