from django.contrib import admin
from customer.models import Customer, Provider, Product
from users.admin_tags import admin_tag_user_link

class ProviderAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'company',    
    )
    
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'silver_id',
        'user_link',
        'first_name',
        'last_name',
        'company',
        'email',    
    )

    def user_link(self, obj):
        try:
            return admin_tag_user_link(obj.user.pk)
        except AttributeError:
            return
    
    user_link.short_description = 'User'

admin.site.register(Customer, CustomerAdmin)
admin.site.register(Provider, ProviderAdmin)
admin.site.register(Product)

# Register your models here.
