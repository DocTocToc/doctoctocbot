from django.contrib import admin
from customer.models import Customer, Provider

class ProviderAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'company',    
    )

admin.site.register(Customer)
admin.site.register(Provider, ProviderAdmin)

# Register your models here.
