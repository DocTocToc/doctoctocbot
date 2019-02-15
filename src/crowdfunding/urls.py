from django.urls import include, path, re_path
from django.views.generic import TemplateView

from crowdfunding import views2
from crowdfunding.views import index, show_checkout, new_checkout, create_checkout
from crowdfunding.views2 import process_payment, InvestView, payment_done


app_name = 'crowdfunding'


urlpatterns = [
    path('', index, name="index"),
    path('checkouts/new', new_checkout, name="new-checkout"),
    path('checkouts/<transaction_id>', show_checkout, name="show-checkout"),
    re_path('checkouts/', create_checkout, name="create-checkout"),
    path('presentation/', TemplateView.as_view(template_name="crowdfunding/crowdfunding.html")),
    path('home/', InvestView.as_view(), name="get-amount"),
    #re_path('pay/(?P<amount>\d+)', views2.process_payment, name="pay"),
    path('pay/', process_payment, name="pay"),
    #re_path('braintree/(?P<amount>\d+)', CheckoutView.as_view(), name="braintree"),
    #re_path(r'^braintree/(?:(?P<amount>\d+)/)?$', CheckoutView.as_view(), name="braintree"),
    re_path('ok/(?P<amount>\d+)', TemplateView.as_view(template_name="crowdfunding/ok.html"), name='crowdfunding-ok'),
    path('paypal/', include('paypal.standard.ipn.urls'), name="paypal-ipn"),
    path('payment-done/', payment_done, name='payment_done'),
    path('payment-cancelled/', views2.payment_canceled, name='payment_cancelled'),
]