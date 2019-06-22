from django.contrib import admin
from .models import BlogPage


class BlogPageAdmin(admin.ModelAdmin):
    autocomplete_fields = ['authors']

admin.site.register(BlogPage, BlogPageAdmin)