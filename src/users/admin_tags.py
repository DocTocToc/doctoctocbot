from django.contrib.auth import get_user_model
from django.utils.safestring import mark_safe
from django.urls import reverse
from constance import config
from moderation.models import SocialMedia

User = get_user_model()

def admin_tag_user_link(du: User):
    """ Return Django User admin html link tag from User object
    """
    if du:
        somed= config.local_social_media
        try:
            emoji = SocialMedia.objects.get(name=somed).emoji
        except SocialMedia.DoesNotExist:
            emoji = None
        return mark_safe(
            '<a href="{link}">{tag}</a>'.format(
                link = reverse("admin:users_user_change", args=(du.pk,)),
                tag = f'{emoji}{du.username}'
            )
        )