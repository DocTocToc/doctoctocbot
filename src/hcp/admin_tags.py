from moderation.models import SocialUser
from hcp.models import HealthCareProvider, Taxonomy

from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.urls import reverse

import logging

logger=logging.getLogger(__name__)

def taxonomy_tag(su: SocialUser):
    def get_tag(taxonomy):
        tag_lst = [taxonomy.classification, taxonomy.specialization]
        return " - ".join(filter(None, tag_lst))
    if su is None:
        return
    human = su.human_set.first()
    logger.debug(f'{human=}')
    entity = su.entity
    logger.debug(f'{entity=}')
    taxonomy_lst: list[Taxonomy] = []
    try:
        entities = entity.healthcareprovider.taxonomy.all()
        logger.debug(entities)
        taxonomy_lst.extend(entities)
    except AttributeError:
        pass
    try:
        entities=human.healthcareprovider.taxonomy.all()
        logger.debug(entities)
        taxonomy_lst.extend(entities)
    except AttributeError:
        pass
    logger.debug(f'{taxonomy_lst=}')
    if not taxonomy_lst:
        return
    if len(taxonomy_lst)==1:
        return get_tag(taxonomy_lst[0])
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

def healthcareprovider_link(hcp):
    """ Return HealthCareProvider admin link tag from HealthCareProvider object
    """
    taxonomies = hcp.taxonomy.all()
    if taxonomies:
        tags=[]
        for t in taxonomies:
            tags.append(t.specialization or t.classification)
        return mark_safe(
            '<a href="{link}">{content}</a>'.format(
                link = reverse("admin:hcp_healthcareprovider_change", args=(hcp.pk,)),
                content = f'🧑‍⚕️{", ".join(tags)}'
            )
        )

def hcp_admin_link(entity):
    if not entity:
        return "Add an Entity to this SocialUser."
    try:
        hcp = HealthCareProvider.objects.filter(entity=entity).first()
    except HealthCareProvider.DoesNotExist:
        hcp=None
    if hcp:
        url = reverse("admin:hcp_healthcareprovider_change", args=(hcp.id,))
        txt = "hcp change"
    else:
        url = f"/admin/hcp/healthcareprovider/add/?entity={entity.id}"
        txt = "hcp add"
    return mark_safe(
        f'<a href="{url}">{txt}</a>'
    ) 