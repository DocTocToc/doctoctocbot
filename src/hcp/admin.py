import logging

from django.contrib import admin

from hcp.models import (
    Taxonomy,
    HealthCareProvider,
    HealthCareProviderTaxonomy,
    TaxonomyCategory
)
from modeltranslation.admin import TranslationAdmin
from moderation.models import Human, SocialUser
from moderation.admin_tags import socialmedia_account, entity

logger = logging.getLogger(__name__)

class HealthCareProviderTaxonomyInline(admin.TabularInline):
    model = HealthCareProviderTaxonomy
    extra = 1
    fk_name = 'healthcareprovider'
    readonly_fields = ['healthcareprovider', 'created', 'updated',]
    autocomplete_fields = ['healthcareprovider', 'taxonomy',]


    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "creator":
            creator_ids = []
            try:
                hcp_id: int = int(request.resolver_match.kwargs['object_id'])
            except (AttributeError, KeyError):
                try:
                    human_id: str =request.GET.get('human')
                except (AttributeError, KeyError):
                    pass
                else:
                    creator_ids.append(int(human_id))
            else:
                try:
                    creator_ids.extend(
                        list(
                            HealthCareProviderTaxonomy.objects \
                            .filter(healthcareprovider__id=hcp_id) \
                            .values_list("creator__id", flat=True)
                        )
                    )
                except TypeError:
                    pass
                # append Human id of HealthCareProvider for self moderation
                try:
                    hcp = HealthCareProvider.objects.get(id=hcp_id)
                    creator_ids.append(hcp.human.id)
                except HealthCareProvider.DoesNotExist:
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
        'id',
        'code',
        'grouping_en',
        'classification_en',
        'specialization_en',
        'definition_en',
    )
    fields = (
        'id',
        'code',
        'grouping',
        'classification',
        'specialization',
        'definition',
    )
    readonly_fields = (
        'id',
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
        'id',
        'entity_tag',
        'human',
        'somed_account_tag',
        'taxonomy_tag',
        'created',
        'updated',
        'entity',
    )
    fields = (
        'id',
        'entity_tag',
        'entity',
        'human',
        'created',
        'updated',
    )
    readonly_fields = (
        'id',
        'entity_tag',
        'created',
        'updated',
    )
    search_fields = (
        'taxonomy__code',
        'taxonomy__classification_en',
        'taxonomy__specialization_en',
    )
    inlines = (HealthCareProviderTaxonomyInline,)

    autocomplete_fields = ['human', 'entity']

    def entity_tag(self, obj):
        return entity(obj.entity)

    entity_tag.short_description = 'Entity'
    entity_tag.admin_order_field = 'entity'

    def taxonomy_tag(self, obj):
        return " | ".join( [str(taxonomy) for taxonomy in obj.taxonomy.all()] )

    taxonomy_tag.short_description = 'Taxonomy'
    
    def somed_account_tag(self, obj):
        su_id_lst = [su.id for su in obj.human.socialuser.all()]
        try:
            su = SocialUser.objects.filter(id__in=su_id_lst).latest()
        except SocialUser.DoesNotExist:
            return
        return socialmedia_account(su)
    
    somed_account_tag.short_description = 'SoMed'



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
