from django.contrib import admin
from customer.models import Customer, Provider, Product

class ProviderAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'company',    
    )

admin.site.register(Customer)
admin.site.register(Provider, ProviderAdmin)
admin.site.register(Product)

# Register your models here.
