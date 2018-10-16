from django.contrib import admin

from .models import SocialUser, UserCategoryRelationship, Category

class CategoryRelationshipInline(admin.TabularInline):
    model = UserCategoryRelationship
    extra = 10
    fk_name = 'category'
    
class UserRelationshipInline(admin.TabularInline):
    model = UserCategoryRelationship
    extra = 10
    fk_name = 'social_user'

class SocialUserAdmin(admin.ModelAdmin):
    inlines = (UserRelationshipInline,)

class CategoryAdmin(admin.ModelAdmin):
    inlines = (CategoryRelationshipInline,)

admin.site.register(Category, CategoryAdmin)
admin.site.register(SocialUser, SocialUserAdmin)