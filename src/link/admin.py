from django.contrib import admin

from .models import Link, Website
from django.db.models import Count

class LinkAdmin(admin.ModelAdmin):
    model= Link
    filter_horizontal = ('status', 'socialuser',)
    list_display = ('url', 'website', 'status_count',)
    readonly_fields = ('url', 'website', 'status', 'socialuser', 'status_count',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _status_count=Count("status", distinct=True),
        )
        return queryset
    
    def status_count(self, obj):
        return obj.status.all().count()

    status_count.admin_order_field = '_status_count'

class WebsiteAdmin(admin.ModelAdmin):
    model= Website
    list_display = ('network_location', 'link_count',)
    fields = ('network_location', 'link_count',)
    readonly_fields = ('network_location', 'link_count',)
    ordering = ('network_location',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _link_count=Count("links", distinct=True),
        )
        return queryset
    
    def link_count(self, obj):
        return obj.links.all().count()

    link_count.admin_order_field = '_link_count'


admin.site.register(Link, LinkAdmin)
admin.site.register(Website, WebsiteAdmin)