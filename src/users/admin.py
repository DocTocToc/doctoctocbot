from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import Group

from django.contrib.auth import get_user_model

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
        'is_active',
        'socialuser',
    )
    #list_filter = ('is_superuser',)
    fieldsets = (
        (None, {'fields': ('username', 'email', 'first_name', 'last_name' , 'password')}),
        ('Permissions', {'fields': ('is_superuser','is_active',)}),
        ('Social User', {'fields': ('socialuser',)}),

    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email','password',)}
         ),
    )
    autocomplete_fields = ['socialuser']
    search_fields = (
        'email',
        'username',
        'socialuser',
        'last_name',
        'first_name',
    )
    ordering = ('email',)
    filter_horizontal = ()

admin.site.register(User, CustomUserAdmin)