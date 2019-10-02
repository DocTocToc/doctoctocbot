from django.contrib import admin
from mesh.models import Mesh
from django.utils.safestring import mark_safe
# Register your models here.
class MeshAdmin(admin.ModelAdmin):
    list_display = (
        'uid',
        'mesh_link', 
        'fr',
        'en',
    )
    search_fields = (
        'uid',
        'fr',
        'en'
    )
    fields = (
        'uid',
        'mesh_link', 
        'fr',
        'en',
    )
    readonly_fields = (
        'uid',
        'mesh_link', 
        'en',
    )
    
    def mesh_link(self, obj):
        return mark_safe(
            '<a href="https://meshb.nlm.nih.gov/record/ui?ui={uid}">🔗MeSH</a>'.format(
                uid = obj.uid)
        )
    mesh_link.short_description = "MeSH link"

admin.site.register(Mesh, MeshAdmin)