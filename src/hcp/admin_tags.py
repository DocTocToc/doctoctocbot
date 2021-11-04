from moderation.models import SocialUser

from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.urls import reverse

def taxonomy_tag(su: SocialUser):
    def get_tag(taxonomy):
        tag_lst = [taxonomy.classification, taxonomy.specialization]
        return " - ".join(filter(None, tag_lst))
    if su is None:
        return
    human = su.human_set.first()
    try:
        taxonomy_lst = human.healthcareprovider.taxonomy.all()
    except AttributeError:
        return
    if not taxonomy_lst:
        return
    if len(taxonomy_lst)==1:
        return get_tag(taxonomy_lst.first())
    else:
        tag_lst = ["<ul>"]
        for taxonomy in taxonomy_lst:
            tag_lst.append(
                f"<li>{get_tag(taxonomy)}</li>"
            )
        tag_lst.append("</ul>")
        return mark_safe(
            "".join(tag_lst)
        )