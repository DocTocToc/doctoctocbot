from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import Group

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.safestring import mark_safe

User = get_user_model()


class SocialUser(admin.ModelAdmin):
    search_fields = ['profile__json__screen_name', 'profile__json__name',]


class CustomUserAdmin(UserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = (
        'username',
        'email',
        'last_name',
        'first_name',
        'is_superuser',
        'is_staff',
        'is_active',
        'socialuser',
        'date_joined',
        'last_login',
        'has_social_auth',
        'social_auth_link_tag',
        'entity',
    )
    readonly_fields = (
        'date_joined',
        'last_login',
        'social_auth_link_tag',
    )
    #list_filter = ('is_superuser',)
    fieldsets = (
        (None, {
            'fields': (
                'username',
                'email',
                'first_name',
                'last_name',
                'password',
                'date_joined',
                'last_login',
            )
        }),
        ('Permissions', {
            'fields': ('is_superuser', 'is_staff', 'is_active',)
            }
        ),
        ('Social User', {
            'fields': ('socialuser',)
            }
        ),
        ('Entity', {
            'fields': ('entity',)
            }
        ),
        ('Social auth', {
            'fields': ('social_auth_link_tag',)    
            }
        ),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'fields': (
                'username',
                'email',
                'password1',
                'password2',
                'socialuser',
            )
            }
         ),
    )
    autocomplete_fields = [
        'socialuser',
        'entity'
    ]
    search_fields = (
        'email',
        'username',
        'socialuser__user_id',
        'socialuser__profile__json__name',
        'socialuser__profile__json__screen_name',
        'last_name',
        'first_name',
    )
    ordering = ('email',)
    filter_horizontal = ()

    def has_social_auth(self, obj):
        return bool(obj.social_auth.all())

    has_social_auth.boolean = True
    
    def social_auth_link_tag(self, obj):
        if not obj.social_auth.all():
            return
        links = []
        for sa in obj.social_auth.all():
            try:
                screen_name = sa.extra_data["access_token"]["screen_name"]
            except:
                screen_name = None
            url = reverse(
                "admin:social_django_usersocialauth_change",
                args=[sa.id]
            )
            text = ' '.join(filter(None, (sa.provider, screen_name)))
            links.append(f'<a href="{url}">{text}</a>')
        return mark_safe(
            "</br>".join(links)
        )
    social_auth_link_tag.short_description = "Social auth"


admin.site.register(User, CustomUserAdmin)