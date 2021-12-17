from __future__ import absolute_import

from django.conf.urls import include, url
from silver.views import (
    pay_transaction_view, complete_payment_view
)

urlpatterns = [
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
    url(r'pay/(?P<token>[0-9a-zA-Z-_\.]+)/$',
        pay_transaction_view, name='payment'),
    url(r'pay/(?P<token>[0-9a-zA-Z-_\.]+)/complete$',
        complete_payment_view, name='payment-complete'),
]