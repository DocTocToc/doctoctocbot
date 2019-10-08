from django.contrib import admin
from community.models import Community, Retweet, Trust, Cooperation, CommunityCategoryRelationship


class TrustInline(admin.TabularInline):
    model = Trust
    extra = 5
    fk_name = 'from_community'


class CooperationInline(admin.TabularInline):
    model = Cooperation
    extra = 5
    fk_name = 'from_community'
    
class CategoryInline(admin.TabularInline):
    model = CommunityCategoryRelationship
    extra = 5
    fk_name = 'community'


class CommunityAdmin(admin.ModelAdmin):
    inlines = [
        TrustInline,
        CooperationInline,
        CategoryInline,
    ]
    list_display = (
        'name',
        'active',
        'account',
        'created',
        'site',
    )
    fields = (
        'name',
        'active',
        'account',
        'hashtag',
        'membership',
        'created',
        'site',
        'crowdfunding',
    )
    readonly_fields = (
        'created',
    )
    

class RetweetAdmin(admin.ModelAdmin):
    list_display = (
        'community',
        'hashtag',
        'category',
        'retweet',  
    )

admin.site.register(Community, CommunityAdmin)
admin.site.register(Retweet, RetweetAdmin)