from django.contrib import admin
from filter.models import Word, Filter

class WordAdmin(admin.ModelAdmin):
    list_display = (
        'name',
    )


class FilterAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'active',
        'expression',
    )

admin.site.register(Word, WordAdmin)
admin.site.register(Filter, FilterAdmin)

