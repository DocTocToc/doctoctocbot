import logging

from django.contrib import admin

from hcp.models import (
    Taxonomy,
    HealthCareProvider,
    HealthCareProviderTaxonomy,
    TaxonomyCategory
)
from modeltranslation.admin import TranslationAdmin
from moderation.models import Human

logger = logging.getLogger(__name__)

"""
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
"""


class HealthCareProviderTaxonomyInline(admin.TabularInline):
    model = HealthCareProviderTaxonomy
    extra = 5
    fk_name = 'healthcareprovider'
    readonly_fields = ['healthcareprovider', 'created', 'updated',]
    autocomplete_fields = ['healthcareprovider', 'taxonomy', 'creator',]


    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "creator":
            creator_ids = []
            try:
                parent_id = request.resolver_match.kwargs['object_id']
            except KeyError:
                parent_id = None
            if parent_id:
                try:
                    creator_ids.extend(
                        list(
                            HealthCareProviderTaxonomy.objects \
                            .filter(creator__id=parent_id) \
                            .values_list("creator__id", flat=True)
                        )
                    )
                except TypeError:
                    pass
            if request.user.socialuser:
                creator_ids.extend(
                    request.user.socialuser.human_set.values_list(
                        "id",
                        flat=True
                    )
                )
            kwargs["queryset"] = Human.objects.filter(
                    id__in=creator_ids
                )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class HealthCareProviderInline(admin.TabularInline):
    model = HealthCareProviderTaxonomy
    extra = 10
    fk_name = 'healthcareprovider'
    raw_id_fields = ("healthcareprovider",)
    readonly_fields = (
        'healthcareprovider',
        'created',
        'updated',
    )
    autocomplete_fields = ['taxonomy', 'creator',]


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
        'grouping_en',
        'classification_en',
        'specialization_en',
        'definition_en',
    )


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
    inlines = (HealthCareProviderTaxonomyInline,)

    autocomplete_fields = ['human']


    def taxonomy_tag(self, obj):
        return " ".join( [str(taxonomy) for taxonomy in obj.taxonomy.all()] )

    taxonomy_tag.short_description = 'Taxonomy'


class TaxonomyCategoryAdmin(admin.ModelAdmin):
    list_display = (
        'code',
        'grouping',
        'classification',
        'specialization',
        'category',
        'community',
    )
    readonly_fields = (
        'code',
    )
    search_fields = (
        'code',
        'grouping',
        'classification',
        'specialization',
        'category',
    )


admin.site.register(Taxonomy, TaxonomyAdmin)
admin.site.register(HealthCareProvider, HealthCareProviderAdmin)
admin.site.register(TaxonomyCategory, TaxonomyCategoryAdmin)
