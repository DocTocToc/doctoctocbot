from moderation.models import SocialUser, MastodonUser, SocialMedia, Entity

from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.utils.safestring import SafeString
from django.core.exceptions import ObjectDoesNotExist
from users.admin_tags import admin_tag_user_link
from hcp.admin_tags import healthcareprovider_link

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

def screen_name_link_su(su):
    """ Return SocialUser screen name html link tag from SocialUser id
    """
    if su:
        try:
            emoji = su.social_media.emoji
        except:
            emoji = ''
        return mark_safe(
            '<a href="{link}">{tag}</a>'.format(
                link = reverse("admin:moderation_socialuser_change", args=(su.pk,)),
                tag = f'{emoji}{su.screen_name_tag()}'
            )
        )

def acct_link_mu(mu):
    """ Return MastodonUser screen name html link tag from MastodonUser object
    """
    if mu:
        try:
            emoji = SocialMedia.objects.get(name="Mastodon").emoji
        except:
            emoji = ''
        return mark_safe(
            '<a href="{link}">{tag}</a>'.format(
                link = reverse("admin:moderation_mastodonuser_change", args=(mu.pk,)),
                tag = f'{emoji}{mu.acct}'
            )
        )

def webfinger(mu: MastodonUser) -> SafeString:
    """ Return Webfinger html link tag from MastodonUser object
    """
    try:
        username, host = mu.acct.split('@')
    except:
        return
    return mark_safe(
        '<a href="{link}">👉</a>'.format(
                link = f"https://{host}/users/{username}"
            )
        )

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

def m2m_field_tag(m2m_field):
    return mark_safe(
        "<br />".join(
            [str(obj) for obj in m2m_field.all()]
        )
    )

def entity(e: Entity):
    if e:
        socialusers = [
            screen_name_link_su(su) for su in e.socialuser_set.all()
        ]
        djangousers = [
            admin_tag_user_link(user) for user in e.user_set.all()
        ]
        mastodonusers = [
            acct_link_mu(mu) for mu in e.mastodonuser_set.all()]
        try:
            hcp = f"<br>{healthcareprovider_link(e.healthcareprovider)}"
        except ObjectDoesNotExist:
            hcp = ''
        entity_link = (
            '<a href="{link}">Entity {eid}</a>'.format(
                link=reverse("admin:moderation_entity_change",
                    args=(e.id,)),
                eid=e.id
            )
        )
        return mark_safe(
            f"{entity_link}"
            f"{('<br>' + ', '.join(socialusers)) if socialusers else ''}"
            f"{('<br>' + ', '.join(mastodonusers)) if mastodonusers else ''}"
            f"{('<br>' + ', '.join(djangousers)) if djangousers else ''}"
            f"{hcp}"
        )