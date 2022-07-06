from django.contrib import admin
from filter.models import Word, Filter
from moderation.admin_tags import m2m_field_tag

class WordAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'word',
    )


class FilterAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'active',
        'word_tag',
        'expression',
        'community_tag',
    )

    def word_tag(self, obj):
        return m2m_field_tag(obj.word)

    word_tag.short_description = 'Word'

    def community_tag(self, obj):
        return m2m_field_tag(obj.community)

    community_tag.short_description = 'Community'


admin.site.register(Word, WordAdmin)
admin.site.register(Filter, FilterAdmin)