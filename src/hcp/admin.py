import logging

from django.contrib import admin

from hcp.models import (
    Taxonomy,
    HealthCareProvider,
    HealthCareProviderTaxonomy,
    TaxonomyCategory
)
from modeltranslation.admin import TranslationAdmin
from moderation.models import Entity, SocialUser, MastodonUser
from moderation.admin_tags import socialmedia_account, entity, webfinger
from django.utils.safestring import mark_safe

logger = logging.getLogger(__name__)

class HealthCareProviderTaxonomyInline(admin.TabularInline):
    model = HealthCareProviderTaxonomy
    extra = 1
    fk_name = 'healthcareprovider'
    readonly_fields = ['healthcareprovider', 'created', 'updated',]
    autocomplete_fields = ['healthcareprovider', 'taxonomy',]
    raw_id_fields = (
        'creator',
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "creator_entity":
            creator_entity_ids = []
            try:
                hcp_id: int = int(request.resolver_match.kwargs['object_id'])
            except (AttributeError, KeyError):
                try:
                    entity_id: str =request.GET.get('entity')
                except (AttributeError, KeyError):
                    pass
                else:
                    if entity_id:
                        creator_entity_ids.append(int(entity_id))
            else:
                try:
                    creator_entity_ids.extend(
                        list(
                            HealthCareProviderTaxonomy.objects \
                            .filter(healthcareprovider__id=hcp_id) \
                            .values_list("creator_entity__id", flat=True)
                        )
                    )
                except TypeError:
                    pass
                # append Entity id of HealthCareProvider for self moderation
                try:
                    hcp = HealthCareProvider.objects.get(id=hcp_id)
                    try:
                        creator_entity_ids.append(hcp.entity.id)
                    except:
                        pass 
                except HealthCareProvider.DoesNotExist:
                    pass
            try:
                creator_entity_ids.append(request.user.socialuser.entity.id)
            except:
                pass
            kwargs["queryset"] = Entity.objects.filter(
                id__in=creator_entity_ids
                )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


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
        'taxonomy_tag',
        'entity_tag',
        'human',
        'twitter_account_tag',
        'mastodon_account_tag',
        'created',
        'updated',
        'entity',
    )
    fields = (
        'id',
        'taxonomy_tag',
        'entity_tag',
        'entity',
        'human',
        'mastodon_account_tag',
        'created',
        'updated',
    )
    readonly_fields = (
        'id',
        'taxonomy_tag',
        'entity_tag',
        'mastodon_account_tag',
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
        if not obj.entity:
            return "⚠️ No entity"
        return entity(obj.entity)

    entity_tag.short_description = 'Entity'
    entity_tag.admin_order_field = 'entity'

    def taxonomy_tag(self, obj):
        return " | ".join( [str(taxonomy) for taxonomy in obj.taxonomy.all()] )

    taxonomy_tag.short_description = 'Taxonomy'
    
    def twitter_account_tag(self, obj):
        su_ids = []
        if obj.human:
            su_ids.extend([su.id for su in obj.human.socialuser.all()])
        if obj.entity:
            try:
                su_ids.extend([su.id for su in obj.entity.socialuser.all()])
            except AttributeError:
                pass
        try:
            su_qs = SocialUser.objects.filter(id__in=su_ids)
        except SocialUser.DoesNotExist:
            return
        return mark_safe(
            ", ".join(socialmedia_account(su) for su in su_qs)
        )
    
    twitter_account_tag.short_description = 'Twitter'

    def mastodon_account_tag(self, obj):
        accts = []
        if obj.entity:
            try:
                accts.extend([mu.acct for mu in obj.entity.mastodonuser_set.all()])
            except AttributeError:
                pass
        try:
            mu_qs = MastodonUser.objects.filter(acct__in=accts)
        except MastodonUser.DoesNotExist:
            return
        return mark_safe(
            ", ".join(webfinger(mu) for mu in mu_qs)
        )

    mastodon_account_tag.short_description = 'Mastodon'


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

@admin.register(HealthCareProviderTaxonomy)
class HealthCareProviderCategory(admin.ModelAdmin):
    raw_id_fields = (
        'creator',
        'creator_entity',
    )


admin.site.register(Taxonomy, TaxonomyAdmin)
admin.site.register(HealthCareProvider, HealthCareProviderAdmin)
admin.site.register(TaxonomyCategory, TaxonomyCategoryAdmin)
