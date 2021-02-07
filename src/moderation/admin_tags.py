from moderation.models import SocialUser

from django.utils.html import format_html

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
            if su.user_id == relation.moderator.user_id:    
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