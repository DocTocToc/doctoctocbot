from django.contrib import admin
from django.db.models import Count
from versions.admin import VersionedAdmin
from django.utils.safestring import mark_safe
from django.urls import reverse
from .models import (
    SocialUser,
    UserCategoryRelationship,
    Category,
    Profile,
    Queue,
    Moderation,
    TwitterList,
    Follower,
    Moderator,
    Image,
    DoNotRetweet
)


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
    )

    
class UserRelationshipInline(admin.TabularInline):
    model = UserCategoryRelationship
    extra = 10
    fk_name = 'social_user'
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "moderator":
            kwargs["queryset"] = SocialUser.objects.filter(id=request.user.socialuser.id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class SocialUserAdmin(admin.ModelAdmin):
    inlines = (UserRelationshipInline,)
    list_display = ('pk', 'user_id', 'screen_name_tag', 'mini_image_tag',  'name_tag',  'social_media_profile', )
    fields = ('pk', 'screen_name_tag', 'normal_image_tag', 'name_tag', 'user_id', 'social_media_profile', 'category', 'category_moderator_lst')
    readonly_fields = ('pk', 'screen_name_tag', 'normal_image_tag', 'name_tag', 'user_id', 'social_media_profile', 'category', 'category_moderator_lst')
    search_fields = ('user_id', 'profile__json',)
    
    def category_moderator_lst(self, obj):
        cat_mod_lst = []
        for relation in obj.categoryrelationships.all():
            cat_mod_lst.append((relation.category.name, relation.moderator.screen_name_tag(),))
        return cat_mod_lst
    
    def social_media_profile(self, obj):
        return mark_safe(
            '<a href="https://twitter.com/intent/user?user_id={user_id}">{tag}</a>'.format(
                user_id = obj.user_id,
                tag = obj.social_media
            )
        )

    
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'label', 'description', 'show_relationships_count',
                    'quickreply', 'socialgraph', 'color',)
    inlines = (CategoryRelationshipInline,)
    fields = ('name', 'label', 'quickreply', 'socialgraph', 'show_relationships_count', 'description','color',)
    
    def get_queryset(self, request):
        qs = super(CategoryAdmin, self).get_queryset(request)
        return qs.annotate(relationships_count=Count('relationships'))

    def show_relationships_count(self, inst):
        return inst.relationships_count
    
    show_relationships_count.admin_order_field = '-relationships_count'    
    show_relationships_count.short_description = 'Count'
    readonly_fields = ('name', 'show_relationships_count',)
    
class QueueAdmin(VersionedAdmin):
    list_display = ('mini_image_tag', 'screen_name_link', 'name_tag', 'user_id', 'status_tag', 'status_link',)
    readonly_fields = ('mini_image_tag', 'screen_name_link', 'name_tag', 'user_id', 'status_tag','status_link',)
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
    

    def status_link(self, obj):
        return mark_safe(
            '<a href="https://twitter.com/{screen_name}/status/{status_id}" target="_blank">{status_id}</a>'.format(
                screen_name = obj.screen_name_tag(),
                status_id = obj.status_id
            )
        )

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('mini_image_tag', 'screen_name_tag', 'name_tag', 'socialuser',)
    fields = ('mini_image_tag', 'screen_name_tag', 'name_tag', 'socialuser', 'json', 'updated', 'normalavatar',)
    readonly_fields = ('mini_image_tag', 'screen_name_tag', 'name_tag', 'socialuser', 'json', 'updated', 'normalavatar',)


class ModerationAdmin(VersionedAdmin):
    pass
    list_display = ('moderator_mini_image_tag', 'moderator_screen_name_tag', 'moderated_mini_image_tag', 'screen_name_link', 'status_tag', 'status_link',)
    fields = ('moderator_mini_image_tag',
              'moderator_screen_name_tag',
              'moderated_mini_image_tag',
              'screen_name_link',
              'status_tag',
              'status_link',
              'id',
              'identity',
              )
    readonly_fields = ('moderator_mini_image_tag', 'moderator_screen_name_tag', 'moderated_mini_image_tag', 'screen_name_link', 'status_tag', 'status_link',)
    list_display_show_identity = True
    list_display_show_end_date = True
    list_display_show_start_date = True
    
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
    
    def status_link(self, obj):
        return mark_safe(
            '<a href="https://twitter.com/{screen_name}/status/{status_id}" target="_blank">🐦</a>'.format(
                screen_name = obj.moderated_screen_name_tag(),
                status_id = obj.queue.status_id
            )
        )

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
        'followers',
        'created'
    )

class ModeratorAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'socialuser',
        'active',
        'public',
    )
    fields = (
        'pk',
        'socialuser',
        'active',
        'public',
    )
    readonly_fields = (
        'pk',
        'socialuser',
    )

admin.site.register(Category, CategoryAdmin)
admin.site.register(SocialUser, SocialUserAdmin)

admin.site.register(Profile, ProfileAdmin)

admin.site.register(Queue, QueueAdmin)
admin.site.register(Moderation, ModerationAdmin)
admin.site.register(TwitterList, TwitterListAdmin)
admin.site.register(Follower, FollowerAdmin)
admin.site.register(Moderator, ModeratorAdmin)
admin.site.register(Image)
admin.site.register(DoNotRetweet)