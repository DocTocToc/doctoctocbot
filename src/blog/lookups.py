from ajax_select import register, LookupChannel
from django.conf import settings
from django.contrib.auth import get_user_model

@register('authors')
class UserLookup(LookupChannel):

    model = get_user_model()

    def get_query(self, q, request):
        return self.model.objects.filter(username=q)

    #def format_item_display(self, item):
    #    return u"<span class='tag'>%s</span>" % item.name