from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework import routers
from customer.api.views import CustomerViewSet, create_invoice
from . import views

app_name = 'customer'

router = routers.DefaultRouter()
router.register(r'customer', CustomerViewSet)

urlpatterns = [
    path('customer/api/invoice/', create_invoice, name='invoice'),
    path('customer/api/', include(router.urls)),
    path('customer/', views.get_customer, name='customer'),
    path('thanks/', TemplateView.as_view(template_name='customer/thanks.html')),
]
