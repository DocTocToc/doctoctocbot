from django.contrib.auth import get_user_model
from django.utils.safestring import mark_safe
from django.urls import reverse

User = get_user_model()

def admin_tag_user_link(pk):
    """ Return Django User html link tag from pk
    """
    try:
        user = User.objects.get(pk=pk)
        return mark_safe(
            '<a href="{link}">{tag}</a>'.format(
                link = reverse("admin:users_user_change", args=(user.pk,)),
                tag = user.username
            )
        )
    except User.DoesNotExist:
        return