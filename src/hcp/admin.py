import logging

from django.contrib import admin

from hcp.models import Taxonomy, HealthCareProvider, HealthCareProviderTaxonomy
from modeltranslation.admin import TranslationAdmin

logger = logging.getLogger(__name__)

class HealthCareProviderTaxonomyInline(admin.TabularInline):
    model = HealthCareProviderTaxonomy
    extra = 10
    fk_name = 'taxonomy'
    raw_id_fields = ("healthcareprovider", "creator",)
    readonly_fields = (
        'healthcareprovider',
        'creator',
        'created',
        'updated',
    )
    
class HealthCareProviderInline(admin.TabularInline):
    model = HealthCareProviderTaxonomy
    extra = 10
    fk_name = 'healthcareprovider'
    raw_id_fields = ("healthcareprovider", "creator",)
    readonly_fields = (
        'healthcareprovider',
        'created',
        'updated',
    )

class TaxonomyAdmin(TranslationAdmin):
    list_display = (
        'code',
        'grouping_en',
        'classification_en',
        'specialization_en',
        'definition_en',
    )
    fields = (
        'code',
        'grouping',
        'classification',
        'specialization',
        'definition',
    )
    readonly_fields = (
        'code',
    )
    search_fields = (
        'code',
        'grouping',
        'classification',
        'specialization',
        'definition',
    )
    inlines = (HealthCareProviderTaxonomyInline,)




class HealthCareProviderAdmin(admin.ModelAdmin):
    list_display = (
        'human',
        'taxonomy_tag',
        'created',
        'updated',
    )
    fields = (
        'human',
        'created',
        'updated',
    )
    readonly_fields = (
        'created',
        'updated',
    )
    search_fields = (
        'human',
    )
    inlines = (HealthCareProviderInline,)

    def taxonomy_tag(self, obj):
        return " ".join( [str(taxonomy) for taxonomy in obj.taxonomy.all()] )

    taxonomy_tag.short_description = 'Taxonomy'


admin.site.register(Taxonomy, TaxonomyAdmin)
admin.site.register(HealthCareProvider, HealthCareProviderAdmin)

