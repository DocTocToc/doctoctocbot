import logging
from django.utils.translation import ugettext_lazy as _
from typing import List,Tuple
from django.contrib import admin
from django.db.models import F, Q
from django.db.models import Count
from versions.admin import VersionedAdmin
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.forms import TextInput, Textarea
from django.db import models
from rangefilter.filter import DateRangeFilter
from conversation.models import Tweetdj
from bot.models import Account
from moderation.models import (
    SocialUser,
    Human,
    UserCategoryRelationship,
    Category,
    Profile,
    Queue,
    Moderation,
    TwitterList,
    Follower,
    Friend,
    Moderator,
    Image,
    DoNotRetweet,
    SocialMedia,
    CategoryMetadata,
)
from community.models import Community
from modeltranslation.admin import TranslationAdmin

logger = logging.getLogger(__name__)


def tweetdj_link(self, obj):
    """
    Return a link to the corresponding Tweetdj object admin page
    """
    if type(obj) is Queue:
        _statusid = obj.status_id
    elif type(obj) is Moderation:
        _statusid = obj.queue.status_id

    if Tweetdj.objects.filter(statusid=_statusid).exists():
        return mark_safe(
            '<a href="{}">🗃️</a>'
            .format(
                reverse("admin:conversation_tweetdj_change", args=(_statusid,))
            )
        )
    else:
        return "❌"


class CategoryRelationshipInline(admin.TabularInline):
    model = UserCategoryRelationship
    extra = 10
    fk_name = 'category'
    raw_id_fields = ("social_user", "moderator",)
    
    def social_user_screen_name_tag(self, obj):
        screen_name = obj.social_user.profile.json.get("screen_name", None)
        return screen_name
    
    def moderator_screen_name_tag(self, obj):
        screen_name = obj.moderator.profile.json.get("screen_name", None)
        return screen_name
    
    moderator_screen_name_tag.short_description = 'Moderator screen name'
    social_user_screen_name_tag.short_description = 'Social User screen name'
    readonly_fields = (
        'social_user_screen_name_tag',
        'moderator_screen_name_tag',
        'created',
        'updated',
    )

    
class UserRelationshipInline(admin.TabularInline):
    model = UserCategoryRelationship
    extra = 10
    fk_name = 'social_user'
    readonly_fields = ['created', 'updated']
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "moderator":
            mod_ids = list(Moderator.objects.values_list('socialuser', flat=True))
            try:
                logger.debug(request.resolver_match.kwargs["object_id"])
                parent_obj_id = request.resolver_match.kwargs["object_id"]
                kwargs["queryset"] = SocialUser.objects.filter(
                    Q(id=parent_obj_id) | Q(id__in=mod_ids)
                )
            except IndexError:
                pass
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class ProtectedFilter(admin.SimpleListFilter):
    title = 'Protected' # a label for our filter
    parameter_name = 'protected' # you can put anything here

    def lookups(self, request, model_admin):
    # This is where you create filter options; we have two:
        return [
            ('unprotected', 'Unprotected'),
            ('protected', 'Protected'),
        ]

    def queryset(self, request, queryset):
    # This is where you process parameters selected by use via filter options:
        if self.value() == 'unprotected':
            return queryset.distinct().filter(profile__json__protected=False)
        if self.value() == 'protected':
            return queryset.distinct().filter(profile__json__protected=True)


class BotFollower(admin.SimpleListFilter):
    title = 'Bot Follower'
    parameter_name = 'follow_bot'
    
    def lookups(self, request, model_admin):
        return list(Account.objects.values_list('userid', 'username'))

    def queryset(self, request, queryset):
        for userid in list(Account.objects.values_list('userid', flat=True)):
            if self.value() == str(userid):
                logger.debug(f"{self.value()=}")
                try:
                    su = SocialUser.objects.get(user_id=userid)
                except SocialUser.DoesNotExist:
                    return SocialUser.objects.none()
                logger.debug(f"{su=}")
                try:
                    followers_ids = Follower.objects.filter(user=su).latest().id_list
                except Follower.DoesNotExist:
                    return SocialUser.objects.none()
                logger.debug(f"{followers_ids=}")
                return queryset.filter(user_id__in=followers_ids)


class SocialUserAdmin(admin.ModelAdmin):
    inlines = (UserRelationshipInline,)
    list_display = (
        'pk',
        'user_id',
        'screen_name_tag',
        'mini_image_tag',
        'name_tag',
        'profile_link',
        'social_media_profile',
    )
    fields = (
        'pk',
        'screen_name_tag',
        'normal_image_tag',
        'name_tag',
        'user_id',
        'profile_link',
        'social_media_profile',
        'category',
        'category_moderator_lst',
    )
    readonly_fields = (
        'pk',
        'screen_name_tag',
        'normal_image_tag',
        'name_tag',
        'user_id',
        'profile_link',
        'social_media_profile',
        'category',
        'category_moderator_lst'
    )
    search_fields = (
        'user_id',
        'profile__json',
    )
    list_filter = (
        'category__name',
        ProtectedFilter,
        BotFollower,
    )

    def category_moderator_lst(self, obj):
        cat_mod_lst = []
        for relation in obj.categoryrelationships.all():
            cat_mod_lst.append((relation.category.name, relation.moderator.screen_name_tag(),))
        return cat_mod_lst
    
    def social_media_profile(self, obj):
        if obj.social_media.name == "twitter":
            return mark_safe(
                '<a href="https://twitter.com/intent/user?user_id={user_id}">{tag}</a>'.format(
                    user_id = obj.user_id,
                    tag = obj.social_media
                )
            )
        elif obj.social_media.name == "santetoctoc":
            return obj.social_media.name

    def profile_link(self, obj):
        try:
            su = Profile.objects.get(socialuser=obj.pk)
            return mark_safe(
                '<a href="{link}">{tag}</a>'.format(
                    link = reverse("admin:moderation_profile_change", args=(su.pk,)),
                    tag = obj.screen_name_tag()
                )
            )
        except Profile.DoesNotExist:
            return "🚫"

    profile_link.short_description = 'Profile'
    
class CategoryAdmin(TranslationAdmin):
    list_display = (
        'name',
        'label_fr',
        'label_en',
        'public',
        'show_relationships_count',
    )
    inlines = (CategoryRelationshipInline,)
    fields = (
        'name',
        'label',
        'description',
        'mesh',
        'field',
        'public',
        'show_relationships_count',
    )
    search_fields = ['name', 'label', 'description', 'field',]
    autocomplete_fields = ['field',]
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size':'72'})},
    }
    
    def get_queryset(self, request):
        qs = super(CategoryAdmin, self).get_queryset(request)
        return qs.annotate(relationships_count=Count('relationships'))

    def show_relationships_count(self, inst):
        return inst.relationships_count
    
    show_relationships_count.admin_order_field = '-relationships_count'    
    show_relationships_count.short_description = 'Count'
    readonly_fields = (
        'name',
        'show_relationships_count',
    )
    
class QueueAdmin(VersionedAdmin):
    list_display = (
        'mini_image_tag',
        'screen_name_link',
        'name_tag',
        'user_id',
        'status_tag',
        'tweet_link',
        'status_object',
        'type',
        'community',
    )
    readonly_fields = (
        'status_id',
        'mini_image_tag',
        'screen_name_link',
        'name_tag',
        'user_id',
        'status_tag',
        'tweet_link',
        'status_object',
        'community',    
    )
    fields = (
        'status_id',
        'mini_image_tag',
        'screen_name_link',
        'name_tag',
        'user_id',
        'status_tag',
        'tweet_link',
        'status_object',
        'type',
        'community',    
    )
    list_display_show_identity = False
    list_display_show_end_date = False
    list_display_show_start_date = True
    
    def screen_name_link(self, obj):
        try:
            su = SocialUser.objects.get(user_id=obj.user_id)
            return mark_safe(
                '<a href="{link}">{tag}</a>'.format(
                    link = reverse("admin:moderation_socialuser_change", args=(su.pk,)),
                    tag = obj.screen_name_tag()
                )
            )
        except SocialUser.DoesNotExist:
            return obj.screen_name_tag()
    
    screen_name_link.short_description = 'SocialUser'
    

    def tweet_link(self, obj):
        return mark_safe(
            '<a href="https://twitter.com/{screen_name}/status/{status_id}" target="_blank"alt="{status_id}">🐦</a>'.format(
                screen_name = obj.screen_name_tag(),
                status_id = obj.status_id
            )
        )
    
    tweet_link.short_description = "Tweet"

    def status_object(self, obj):
        return tweetdj_link(self, obj)
    
    status_object.short_description = "Status"


class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        'mini_image_tag',
        'screen_name_tag',
        'name_tag',
        'socialuser_link',
        'created',
        'updated',
    )
    fields = ('mini_image_tag', 'screen_name_tag', 'name_tag', 'socialuser_link', 'json', 'updated', 'normalavatar', 'biggeravatar', 'miniavatar',)
    readonly_fields = ('mini_image_tag', 'screen_name_tag', 'name_tag', 'socialuser_link', 'json', 'updated', 'normalavatar', 'biggeravatar', 'miniavatar',)
    search_fields = ('json',)
    
    def socialuser_link(self, obj):
        try:
            su = SocialUser.objects.get(pk=obj.socialuser.pk)
            return mark_safe(
                '<a href="{link}">{tag}</a>'.format(
                    link = reverse("admin:moderation_socialuser_change", args=(su.pk,)),
                    tag = obj.screen_name_tag()
                )
            )
        except SocialUser.DoesNotExist:
            return "🚫"

    socialuser_link.short_description = 'SocialUser'


class ModerationStateListFilter(admin.SimpleListFilter):
    title = _('state')
    parameter_name = 'state'
    
    def lookups(self, request, model_admin):
        state: List[Tuple] = list(
            CategoryMetadata.objects.values_list(
                'name',
                'label',
            )
        )
        state.append( ('pending', _('Pending'),) )
        return state

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        elif self.value()=='pending':
            return queryset.filter(state=None)
        else:
            return queryset.filter(
                state__name=self.value()
            )


class CommunityListFilter(admin.SimpleListFilter):
    title = _('community')
    parameter_name = 'queue'
    
    def lookups(self, request, model_admin):
        state: List[Tuple] = list(
            Community.objects.values_list(
                'name',
                'name',
            )
        )
        return state

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        else:
            return queryset.filter(
                queue__community__name=self.value()
            )

class ModerationAdmin(VersionedAdmin):
    list_display = (
        'state',
        'queue_link',
        'queue_type',
        'moderator_mini_image_tag',
        'moderator_screen_name_tag',
        'moderated_mini_image_tag',
        'screen_name_link',
        'status_tag',
        'tweet_link',
        'status_object',
        'community',
    )
    fields = (
        'state',
        'queue_link',
        'queue_type',
        'moderator_mini_image_tag',
        'moderator_screen_name_tag',
        'moderated_mini_image_tag',
        'screen_name_link',
        'status_tag',
        'tweet_link',
        'status_object',
        'id',
        'identity',
    )
    readonly_fields = (
        'queue_link',
        'queue_type',
        'moderator_mini_image_tag',
        'moderator_screen_name_tag',
        'moderated_mini_image_tag',
        'screen_name_link',
        'status_tag',
        'tweet_link',
        'status_object',    
    )
    list_filter = (
        ModerationStateListFilter,
        CommunityListFilter,
        'queue__type',
    )
    list_display_show_identity = True
    list_display_show_end_date = True
    list_display_show_start_date = True
    search_fields = (
        'queue__user_id',
    )
    ordering = ['-version_start_date',]

    def get_search_results(self, request, queryset, search_term):
        # search_term is what you input in admin site
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)

        user_ids = list(
            Profile.objects.filter(
                json__screen_name__icontains=search_term
            ).values_list("json__id", flat=True)
        )
        try:
            user_id = int(search_term)
            user_ids.append(user_id)
        except ValueError:
            pass
        queryset |= self.model.objects.filter(
            queue__user_id__in=user_ids
        )
        return queryset, use_distinct
    
    def queue_type(self, obj):
        type = obj.queue.type or ""
        return type

    queue_type.admin_order_field  = 'queue'  #Allows column order sorting
    queue_type.short_description = 'Queue type'  #Renames column head
    
    def screen_name_link(self, obj):
        try:
            su = SocialUser.objects.get(user_id=obj.queue.user_id)
            return mark_safe(
                '<a href="{link}">{tag}</a>'.format(
                    link = reverse("admin:moderation_socialuser_change", args=(su.pk,)),
                    tag = obj.moderated_screen_name_tag()
                )
            )
        except SocialUser.DoesNotExist:
            return obj.moderated_screen_name_tag()
    
    screen_name_link.short_description = 'Moderated screen_name'

    def queue_link(self, obj):
        try:
            q = Queue.objects.get(id=obj.queue.id)
            return mark_safe(
                '<a href="{link}">Q</a>'.format(
                    link = reverse("admin:moderation_queue_change", args=(q.id,))
                )
            )
        except Queue.DoesNotExist as e:
            logger.error("Queue does not exist.", e)
            return "🚫"
    
    queue_link.short_description = 'Queue'
    
    def status_object(self, obj):
        return tweetdj_link(self, obj)
    
    status_object.short_description = "Status"
    
    def tweet_link(self, obj):
        return mark_safe(
            '<a href="https://twitter.com/{screen_name}/status/{status_id}" target="_blank">🐦</a>'.format(
                screen_name = obj.moderated_screen_name_tag(),
                status_id = obj.queue.status_id
            )
        )
    tweet_link.short_description = "Tweet"
    
    def community(self, obj):
        try:
            return obj.queue.community.name
        except:
            return

    community.short_description = "Community"


class TwitterListAdmin(admin.ModelAdmin):
    list_display = (
        'list_id',
        'slug',
        'name',
        'twitter_description',
        'uid',
        'label',
        'local_description',
        'member_count_tag',
        'community',
    )
    fields = (
        'list_id',
        'slug',
        'name',
        'twitter_description',
        'member_count_tag',
        'uid',
        'label',
        'local_description',
        'json',
        'community',

    )
    readonly_fields = (
        'list_id',
        'slug',
        'name',
        'twitter_description',
        'json',
        'member_count_tag',  
    )
    def member_count_tag(self, obj):
        member_count = obj.json.get("member_count", None)
        return member_count
    
    member_count_tag.short_description = 'Members'

class FollowerAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        '__str__',
        'created'
    )
    readonly_fields = (
        'id',
        'user',
        'id_list',
        'created'
    )


class FriendAdmin(FollowerAdmin):
    pass


#class CommunityInline(admin.TabularInline):
#    model = Moderator.community.through
#    extra = 5

class ModeratorAdmin(admin.ModelAdmin):
#    inlines = [
#        CommunityInline,  
#    ]
    list_display = (
        'pk',
        'socialuser',
        'active',
        'public',
        'senior',
        'community',
    )
    fields = (
        'pk',
        'socialuser',
        'active',
        'public',
        'senior',
        'community',
    )
    readonly_fields = (
        'pk',
    )
    search_fields = ['socialuser',]
    autocomplete_fields = ['socialuser',]
    list_filter = (
        'active',
        'public',
        'senior',
        'community',
    )
"""    
    def community_tag(self, obj):
        return list(obj.community.values_list('name', flat=True))
    
    community_tag.short_description = "Community"
"""

class DoNotRetweetAdmin(admin.ModelAdmin):
    list_display = (
        'socialuser',
        'action',
        'start',
        'stop',
        'moderator',
        'created',
        'updated',
        'current',
        'comment'
    )
    fields = (
        'socialuser',
        'action',
        'start',
        'stop',
        'moderator',
        'created',
        'updated',
        'current',
        'comment'
    )
    readonly_fields = (
        'created',
        'updated',
    )
    list_filter = (
        'current',
        ('start', DateRangeFilter),
        ('stop', DateRangeFilter),
        ('created', DateRangeFilter),
        ('updated', DateRangeFilter),
        'socialuser',
        'moderator',
        'action',

    )
    search_fields = (
        'comment',    
    )


class CategoryMetadataAdmin(TranslationAdmin):
    list_display = (
        'name',
        'label_fr',
        'label_en',
        'dm',
    )
    fields = (
        'name',
        'label',
        'description',
        'dm',
    )
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size':'72'})},
    }

class HumanAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'socialuser_tag',
        'djangouser_tag',
        'created',
        'updated',
    )
    fields = (
        'pk',
        'socialuser',
        'djangouser',
        'created',
        'updated',
    )
    readonly_fields = (
        'pk',
        'created',
        'updated',    
    )
    search_fields = ['socialuser__profile__json__screen_name', 'djangouser__username']
    
    def socialuser_tag(self, obj):
        return [su for su in obj.socialuser.all()]
    
    socialuser_tag.short_description = 'SocialUser'
    
    def djangouser_tag(self, obj):
        return [user for user in obj.djangouser.all()]
    
    djangouser_tag.short_description = 'Django user'

admin.site.register(Category, CategoryAdmin)
admin.site.register(SocialUser, SocialUserAdmin)

admin.site.register(Profile, ProfileAdmin)

admin.site.register(Queue, QueueAdmin)
admin.site.register(Moderation, ModerationAdmin)
admin.site.register(TwitterList, TwitterListAdmin)
admin.site.register(Follower, FollowerAdmin)
admin.site.register(Friend, FriendAdmin)
admin.site.register(Moderator, ModeratorAdmin)
admin.site.register(Image)
admin.site.register(DoNotRetweet, DoNotRetweetAdmin)
admin.site.register(SocialMedia)
admin.site.register(CategoryMetadata, CategoryMetadataAdmin)
admin.site.register(Human, HumanAdmin)