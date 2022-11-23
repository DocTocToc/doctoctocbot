from django.contrib.auth import get_user_model
from django.utils.safestring import mark_safe
from django.urls import reverse

User = get_user_model()

def admin_tag_user_link(du: User):
    """ Return Django User admin html link tag from User object
    """
    if du:
        return mark_safe(
            '<a href="{link}">{tag}</a>'.format(
                link = reverse("admin:users_user_change", args=(du.pk,)),
                tag = du.username
            )
        )