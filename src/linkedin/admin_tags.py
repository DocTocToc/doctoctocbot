from moderation.models import LinkedInUser, SocialMedia
from django.utils.safestring import mark_safe

def linkedin_link(obj: LinkedInUser):
    if obj:
        try:
            emoji = SocialMedia.objects.get(name="LinkedIn").emoji
        except:
            emoji = ''
        return mark_safe(
            '<a href="{link}">{tag}</a>'.format(
                link = f'https://www.linkedin.com/in/{obj.lid}/',
                tag = f'{emoji}{obj.lid}'
            )
        )