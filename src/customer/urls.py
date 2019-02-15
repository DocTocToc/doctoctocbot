from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = 'customer'

urlpatterns = [
    path('customer/', views.get_customer, name='customer'),
    path('thanks/', TemplateView.as_view(template_name='customer/thanks.html')),
]
