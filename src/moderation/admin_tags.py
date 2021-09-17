from moderation.models import SocialUser

from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.urls import reverse

def admin_tag_category(su: SocialUser):
    category_lst = ["<ul>"]
    for relation in su.categoryrelationships.all():
        try:
            screen_name = relation.moderator.screen_name_tag()
        except:
            screen_name = ""
        try:
            category = relation.category.name
        except:
            category = ""
        if category:
            if relation.moderator and su.user_id == relation.moderator.user_id:    
                asterisk = "<span style='color: red'>*</span>"
            else:
                asterisk = ""
            category_lst.append(
                "<li>"
                f"{category}"
                " - "
                f"{screen_name}"
                f"{asterisk}"
                "</li>"
            )
    category_lst.append("</ul>")
    return format_html("".join(category_lst))

def admin_tag_social_user_img(user_id):
    """ Return SocialUser icon html img tag from Twitter user_id
    """
    try:
        return SocialUser.objects.get(user_id=user_id).mini_image_tag()
    except SocialUser.DoesNotExist:
        return


def admin_tag_screen_name_link(user_id):
    """ Return SocialUser screen name html link tag from Twitter user_id
    """
    try:
        su = SocialUser.objects.get(user_id=user_id)
        return mark_safe(
            '<a href="{link}">{tag}</a>'.format(
                link = reverse("admin:moderation_socialuser_change", args=(su.pk,)),
                tag = su.screen_name_tag()
            )
        )
    except SocialUser.DoesNotExist:
        return
    
def screen_name_link_su_pk(su_pk):
    """ Return SocialUser screen name html link tag from Twitter user_id
    """
    try:
        su = SocialUser.objects.get(id=su_pk)
        return mark_safe(
            '<a href="{link}">{tag}</a>'.format(
                link = reverse("admin:moderation_socialuser_change", args=(su_pk,)),
                tag = su.screen_name_tag()
            )
        )
    except SocialUser.DoesNotExist:
        return

def socialmedia_account(su: SocialUser):
    try:
        emoji = su.social_media.emoji
    except:
        emoji = None
    if not emoji:
        emoji = su.social_media.name
    if su.social_media.name == "twitter":
        href = f"https://twitter.com/intent/user?user_id={su.user_id}"
        return mark_safe(
            f'<a href="{href}">{emoji}@{su.screen_name_tag()}</a>'
        )
    else:
        return emoji