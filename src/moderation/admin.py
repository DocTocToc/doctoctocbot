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
    Entity,
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
    ModerationOptIn,
    Prospect,
    Filter,
    MastodonUser,
    LinkedInUser,
)
from hcp.models import HealthCareProvider
from hcp.admin_tags import taxonomy_tag, hcp_admin_link
from linkedin.admin_tags import linkedin_link

from community.models import Community
from moderation.admin_tags import (
    admin_tag_category,
    screen_name_link_su,
    acct_link_mu,
    webfinger,
    entity,
)
from users.admin_tags import admin_tag_user_link
from common.list_filter import by_null_filter
from moderation.admin_tags import m2m_field_tag
from modeltranslation.admin import TranslationAdmin
from django.contrib import auth
from durationwidget.widgets import TimeDurationWidget
from hcp.admin_tags import healthcareprovider_link

logger = logging.getLogger(__name__)

@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    search_fields=[
        'id',
        'socialuser__profile__json__screen_name',
        'mastodonuser__acct',
    ]
    list_display=(
        'id',
        'hcp_tag',
        'socialusers_tag',
        'djangousers_tag',
        'mastodonusers_tag',
        'linkedinusers_tag',
    )
    fields =(
        'id',
        'hcp_tag',
        'socialusers_tag',
        'djangousers_tag',
        'mastodonusers_tag',
        'linkedinusers_tag',
    )
    readonly_fields =(
        'id',
        'hcp_tag',
        'socialusers_tag',
        'djangousers_tag',
        'mastodonusers_tag',
        'linkedinusers_tag',
    )

    def hcp_tag(self, obj):
        return healthcareprovider_link(obj.healthcareprovider)
    hcp_tag.short_description= "HealthCareProvider"

    def socialusers_tag(self, obj):
        return mark_safe(
            "<br>".join(
                [screen_name_link_su(su)
                 for su in obj.socialuser_set.all()]
            )
        )
    socialusers_tag.short_description='Social users'

    def djangousers_tag(self, obj):
        return mark_safe(
            "<br>".join(
                [admin_tag_user_link(du)
                 for du in obj.user_set.all()]
            )
        )
    djangousers_tag.short_description='Django users'

    def mastodonusers_tag(self, obj):
        return mark_safe(
            "<br>".join(
                [acct_link_mu(mu)
                for mu in obj.mastodonuser_set.all()]
            )
        )
    mastodonusers_tag.short_description='Mastodon users'

    def linkedinusers_tag(self, obj):
        return mark_safe(
            "<br>".join(
                [linkedin_link(liu)
                for liu in obj.linkedinuser_set.all()]
            )
        )
    linkedinusers_tag.short_description='LinkedIn users'


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
    extra = 3
    fk_name = 'category'
    raw_id_fields = ("social_user", "moderator",)
    
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "moderator":
            if request.user.socialuser:
                kwargs["queryset"] = SocialUser.objects.filter(
                    id = request.user.socialuser.id
                )
        return super().formfield_for_manytomany(db_field, request, **kwargs)

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
    extra = 3
    fk_name = 'social_user'
    readonly_fields = ['created', 'updated']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "moderator":
            moderator_ids = []
            try:
                parent_id = request.resolver_match.kwargs['object_id']
            except KeyError:
                parent_id = None
            else:
                try:
                    moderator_ids.extend(
                        list(
                            UserCategoryRelationship.objects \
                            .filter(social_user__id=parent_id) \
                            .values_list("moderator__id", flat=True)
                        )
                    )
                except TypeError:
                    pass
                if request.user.socialuser:
                    moderator_ids.append(request.user.socialuser.id)
                # append SocialUser id for self moderation
                moderator_ids.append(parent_id)
                kwargs["queryset"] = SocialUser.objects.filter(
                        id__in=moderator_ids
                    )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class ProtectedFilter(admin.SimpleListFilter):
    title = 'Protected' # a label for our filter
    parameter_name = 'protected' # you can put anything here

    def lookups(self, request, model_admin):
        return [
            ('unprotected', 'Unprotected'),
            ('protected', 'Protected'),
        ]

    def queryset(self, request, queryset):
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
                try:
                    su = SocialUser.objects.get(user_id=userid)
                except SocialUser.DoesNotExist:
                    return SocialUser.objects.none()
                try:
                    followers_ids = Follower.objects.filter(user=su).latest().id_list
                except Follower.DoesNotExist:
                    return SocialUser.objects.none()
                return queryset.filter(user_id__in=followers_ids)


class BotFriend(admin.SimpleListFilter):
    title = 'Bot Friend'
    parameter_name = 'friend_bot'

    def lookups(self, request, model_admin):
        return list(Account.objects.values_list('userid', 'username'))

    def queryset(self, request, queryset):
        for userid in list(Account.objects.values_list('userid', flat=True)):
            if self.value() == str(userid):
                #logger.debug(f"{self.value()=}")
                try:
                    su = SocialUser.objects.get(user_id=userid)
                except SocialUser.DoesNotExist:
                    return SocialUser.objects.none()
                #logger.debug(f"{su=}")
                try:
                    friends_ids = Friend.objects.filter(user=su).latest().id_list
                except Follower.DoesNotExist:
                    return SocialUser.objects.none()
                #logger.debug(f"{friends_ids=}")
                return queryset.filter(user_id__in=friends_ids)


class SocialUserAdmin(admin.ModelAdmin):
    inlines = (UserRelationshipInline,)
    list_display = (
        'id',
        'entity_tag',
        'user_id',
        'mini_image_tag',
        'screen_name_tag',
        'category_tag',
        'socialmedia_tag',
        'name_tag',
        'profile_link',
        'follow_request_tag',
        'block_tag',
        'user_id',
        'hcp_taxonomy_tag',
        'hcp_admin',
        'language',
        'created',
        'updated',
        'entity',
    )
    fields = (
        'entity',
        'screen_name_tag',
        'social_media',
        'socialmedia_tag',
        'normal_image_tag',
        'name_tag',
        'user_id',
        'profile_link',
        'category',
        'category_moderator_lst',
        'follow_request_tag',
        'block_tag',
        'hcp_taxonomy_tag',
        'hcp_admin',
        'human_tag',
        'language',
        'created',
        'updated',
    )
    readonly_fields = (
        'screen_name_tag',
        'socialmedia_tag',
        'normal_image_tag',
        'name_tag',
        'profile_link',
        'category',
        'category_moderator_lst',
        'follow_request_tag',
        'block_tag',
        'hcp_taxonomy_tag',
        'hcp_admin',
        'human_tag',
        'created',
        'updated',
    )
    search_fields = (
        'user_id',
        'profile__json__name',
        'profile__json__screen_name',
        'profile__json__description',
        'entity__mastodonuser__acct',
    )
    list_filter = (
        'category__name',
        ProtectedFilter,
        BotFollower,
        BotFriend,
        by_null_filter('category', 'Category'),
        'social_media',
        'language',
    )
    autocomplete_fields = ['entity']
    def get_queryset(self, request):
        qs = super(SocialUserAdmin, self).get_queryset(request)
        self.request = request
        return qs

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super(SocialUserAdmin, self)\
        .get_readonly_fields(request, obj)
        if obj: # editing an existing object
            return readonly_fields + (
                'user_id',
                'social_media',
            )
        return readonly_fields

    def category_moderator_lst(self, obj):
        cat_mod_lst = []
        for relation in obj.categoryrelationships.all():
            cat_mod_lst.append((relation.category.name, relation.moderator.screen_name_tag(),))
        return cat_mod_lst

    def entity_tag(self, obj):
        return entity(obj.entity)

    entity_tag.short_description = 'Entity'
    entity_tag.admin_order_field = 'entity'

    def profile_link(self, obj):
        try:
            su = Profile.objects.get(socialuser=obj.pk)
            return mark_safe(
                '<a href="{link}">🔗</a>'.format(
                    link = reverse("admin:moderation_profile_change", args=(su.pk,))
                )
            )
        except Profile.DoesNotExist:
            return "🚫"

    profile_link.short_description = 'Profile'

    def follow_request_tag(self, obj):
        # return HTML link that will not be escaped
        tfr = obj.twitter_follow_request.all()
        if not tfr:
            return
        return mark_safe(
            "<br />".join(
                [
                    su.screen_name_tag()
                    for su in tfr
                    if su.screen_name_tag()
                ]
            )
        )
    follow_request_tag.short_description = 'Follow req'

    def block_tag(self, obj):
        # return HTML link that will not be escaped
        return mark_safe(
            "<br />".join(
                [
                    su.screen_name_tag()
                    for su in obj.twitter_block.all()
                ]
            )
        )
    block_tag.short_description = 'Block'
    
    def socialmedia_tag(self, obj):
        try:
            emoji = obj.social_media.emoji
        except:
            return
        if not emoji:
            emoji = obj.social_media.name
        if obj.social_media.name == "twitter":
            href = f"https://twitter.com/intent/user?user_id={obj.user_id}"
            return mark_safe(f'<a href="{href}">{emoji}</a>')
        else:
            return emoji
    socialmedia_tag.short_description = 'SoMed🔗'

    def category_tag(self, obj):
        return admin_tag_category(obj)

    category_tag.short_description = 'Category'

    def hcp_admin(self, obj):
        if obj.entity:
            return hcp_admin_link(obj.entity)
        else:
            return f"Add entity to {obj}"

    hcp_admin.short_description = "hcp admin"

    def hcp_taxonomy_tag(self, obj):
        return taxonomy_tag(obj)

    hcp_taxonomy_tag.short_description = _("Specialty")

    def human_tag(self, obj):
        return mark_safe(
            "\n".join(
                [
                    '<a href="{link}">{tag}</a>'.format(
                        link=reverse(
                            "admin:moderation_human_change", args=(human.id,)
                        ),
                        tag=(
                            "human: {id} {sn}".format(
                                id=human.id,
                                sn=" ".join(
                                    [
                                        f'@{su.screen_name_tag()}'
                                        for su in human.socialuser.all()
                                    ]
                                )
                            )
                        )
                    )
                    for human in obj.human_set.all()
                ]
            )
        )

    human_tag.short_description = "human"


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
    autocomplete_fields = ['mesh', 'field',]
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
    search_fields = (
        'user_id',
    )
    list_display_show_identity = True
    list_display_show_end_date = True
    list_display_show_start_date = True

    def get_ordering(self, request):
        return ['-version_start_date', ] + self.ordering

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

    def get_search_results(self, request, queryset, search_term):
        # search_term is what you input in admin site
        orig_queryset = queryset
        queryset, use_distinct = super(QueueAdmin, self).get_search_results(
            request, queryset, search_term)

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
            user_id__in=user_ids
        )
        queryset = queryset & orig_queryset
        return queryset, use_distinct


class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'mini_image_tag',
        'screen_name_tag',
        'name_tag',
        'socialuser_link',
        'created',
        'updated',
    )
    fields = ('id', 'mini_image_tag', 'screen_name_tag', 'name_tag', 'socialuser_link', 'json', 'updated', 'normalavatar', 'biggeravatar', 'miniavatar',)
    readonly_fields = ('id', 'mini_image_tag', 'screen_name_tag', 'name_tag', 'socialuser_link', 'json', 'updated', 'normalavatar', 'biggeravatar', 'miniavatar',)
    search_fields = (
        'profile__json__name',
        'profile__json__screen_name',
        'profile__json__description',
    )

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
        'queue__community',
        'queue__type',
        'state',
    )
    search_fields = (
        'moderator__profile__json__screen_name',
    )
    list_display_show_identity = True
    list_display_show_end_date = True
    list_display_show_start_date = True

    def get_ordering(self, request):
        #return ['-version_start_date', ] + self.ordering
        return ['-version_start_date', ]

    def get_search_results(self, request, queryset, search_term):
        # search_term is what you input in admin site
        orig_queryset = queryset
        queryset, use_distinct = super(ModerationAdmin, self).get_search_results(
            request, queryset, search_term)

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
        queryset = queryset & orig_queryset
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


class ArrayLength(models.Func):
    function = 'CARDINALITY'


class FollowerAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        '__str__',
        'created',
        'count_tag',
    )
    readonly_fields = (
        'id',
        'user',
        'id_list',
        'created',
        'count_tag',
    )
    list_filter = (
        ('created', DateRangeFilter),
    )
    search_fields = (
        'user__user_id',
        'user__profile__json__screen_name',
        'id_list',
    )

    def get_queryset(self, request):
        qs = super(FollowerAdmin, self).get_queryset(request)
        return qs.annotate(count=ArrayLength('id_list'))

    def count_tag(self, obj):
        return obj.count

    count_tag.short_description = _('Count')
    count_tag.admin_order_field = '-count'


class FriendAdmin(FollowerAdmin):
    def get_queryset(self, request):
        qs = super(FriendAdmin, self).get_queryset(request)
        return qs.annotate(count=ArrayLength('id_list'))


class ModeratorAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'socialuser',
        'active',
        'public',
        'senior',
        'community',
        'created',
        'updated',
    )
    fields = (
        'pk',
        'socialuser',
        'active',
        'public',
        'senior',
        'community',
        'created',
        'updated',
    )
    readonly_fields = (
        'pk',
        'created',
        'updated',
    )
    search_fields = ['socialuser',]
    autocomplete_fields = ['socialuser',]
    list_filter = (
        'active',
        'public',
        'senior',
        'community',
    )


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
    raw_id_fields = (
        'socialuser',
        'moderator',
    )
    search_fields = (
        'comment',    
    )
    list_filter = (
        'current',
        ('start', DateRangeFilter),
        ('stop', DateRangeFilter),
        'action',
    )


class CategoryMetadataAdmin(TranslationAdmin):
    list_display = (
        'name',
        'label_fr',
        'label_en',
        'dm',
        'self_dm',
    )
    fields = (
        'name',
        'label',
        'description',
        'dm',
        'self_dm',
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
        'socialuser_tag',
        'djangouser',
        'djangouser_tag',
        'created',
        'updated',
    )
    readonly_fields = (
        'pk',
        'socialuser_tag',
        'djangouser_tag',
        'created',
        'updated',    
    )
    search_fields = [
        'socialuser__profile__json__screen_name',
        'djangouser__username'
    ]
    raw_id_fields = (
        'djangouser',
        'socialuser',
    )

    def socialuser_tag(self, obj):
        return m2m_field_tag(obj.socialuser)

    socialuser_tag.short_description = 'SocialUser'

    def djangouser_tag(self, obj):
        return m2m_field_tag(obj.djangouser)

    djangouser_tag.short_description = 'Django user'


class SocialMediaAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'emoji',
    )


@admin.register(ModerationOptIn)
class ModerationOptInAdmin(admin.ModelAdmin):
    list_display = (
        'type',
        'option',
        'authorize',
    )


@admin.register(Prospect)
class ProspectAdmin(admin.ModelAdmin):
    list_display = (
        'socialuser',
        'community',
        'active',
        'created',
        'updated',
    )
    list_filter = (
    'community',
    'active',
    )
    search_fields = (
    'socialuser__profile__json',
    )
    
    
@admin.register(Filter)
class FilterAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'active',
        'community',
        'access_protected',
        'account_age',
        'followers_count',
        'member_follower_count',
        'member_follower_ratio',
        'statuses_count',
        'profile_image',
        'profile_update',
    )
    list_filter = (
    'community',
    'active',
    )
    formfield_overrides = {
        models.DurationField: {'widget': TimeDurationWidget},
    }


@admin.register(UserCategoryRelationship)
class UserCategoryRelationshipAdmin(admin.ModelAdmin):
    list_display = [
        'social_user',
        'category',
        'moderator',
        'community',
        'created',
        'updated',
        'active',
    ]
    list_filter = (
        'category',
        'community',
        'active',
    )


@admin.register(MastodonUser)
class MastodonUserAdmin(admin.ModelAdmin):
    list_display = [
        'acct',
        'webfinger_tag',
        'entity_tag',
        'entity',
        'created',
        'updated',
    ]
    fields = [
        'acct',
        'webfinger_tag',
        'entity_tag',
        'hcp_admin',
        'entity',
        'created',
        'updated',
    ]
    readonly_fields = [
        'webfinger_tag',
        'entity_tag',
        'hcp_admin',
        'created',
        'updated',
    ]
    autocomplete_fields = [
        'entity',
    ]
    search_fields = (
        'acct',
        'entity__socialuser__profile__json__screen_name',
    )
    def webfinger_tag(self, obj):
        return webfinger(obj)
    webfinger_tag.short_description = 'Webfinger'

    def entity_tag(self, obj):
        return entity(obj.entity)

    entity_tag.short_description = 'Entity'
    entity_tag.admin_order_field = 'entity'

    def hcp_admin(self, obj):
        if obj.entity:
            return hcp_admin_link(obj.entity)
        else:
            return f"Add entity to {obj}"


@admin.register(LinkedInUser)
class LinkedInUserAdmin(admin.ModelAdmin):
    list_display = [
        'lid',
        'url_tag',
        'entity_tag',
        'entity',
        'created',
        'updated',
    ]
    fields = [
        'lid',
        'url_tag',
        'entity_tag',
        'hcp_admin',
        'entity',
        'created',
        'updated',
    ]
    readonly_fields = [
        'url_tag',
        'entity_tag',
        'hcp_admin',
        'created',
        'updated',
    ]
    autocomplete_fields = [
        'entity',
    ]
    search_fields = (
        'acct',
        'entity__socialuser__profile__json__screen_name',
    )

    def url_tag(self, obj):
        return linkedin_link(obj)
    url_tag.short_description = 'url'

    def entity_tag(self, obj):
        return entity(obj.entity)

    entity_tag.short_description = 'Entity'
    entity_tag.admin_order_field = 'entity'

    def hcp_admin(self, obj):
        if obj.entity:
            return hcp_admin_link(obj.entity)
        else:
            return f"Add entity to {obj}"


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
admin.site.register(CategoryMetadata, CategoryMetadataAdmin)
admin.site.register(Human, HumanAdmin)
admin.site.register(SocialMedia, SocialMediaAdmin)