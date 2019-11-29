from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework import routers
from crowdfunding.api.views import ProjectInvestmentViewSet

#import djstripe
#from crowdfunding.views3 import show_checkout, new_checkout, create_checkout
from crowdfunding.views import stripe_checkout, ProjectInvestmentView, InvestViewBase
from crowdfunding.views import charge
app_name = 'crowdfunding'

router = routers.DefaultRouter()
router.register(r'projectinvestment', ProjectInvestmentViewSet)


urlpatterns = [
    path('', InvestViewBase.as_view(), name='start'),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('presentation/', TemplateView.as_view(template_name="crowdfunding/crowdfunding.html")),
    path('charge/', charge, name='stripe-charge'),
    #path('pay/', process_payment, name="pay"),
    path('pay/', stripe_checkout, name="stripe-checkout"),
    #path('paypal/', include('paypal.standard.ipn.urls'), name="paypal-ipn"),
    #path('payment-done/', payment_done, name='payment_done'),
    #path('payment-cancelled/', payment_canceled, name='payment_cancelled'),
    path('fund/', ProjectInvestmentView.as_view(), name="fund"),
    path('progress/', TemplateView.as_view(template_name='crowdfunding/progress_template.html'), name='progress'),
    #path('stripe/', include("djstripe.urls", namespace="djstripe")),
    #path('checkouts/new', new_checkout, name="new-checkout"),
    #path('checkouts/<transaction_id>', show_checkout, name="show-checkout"),
    #re_path('checkouts/', create_checkout, name="create-checkout"),
    #re_path('braintree/(?P<amount>\d+)', CheckoutView.as_view(), name="braintree"),
    #re_path(r'^braintree/(?:(?P<amount>\d+)/)?$', CheckoutView.as_view(), name="braintree"),
    #re_path('ok/(?P<amount>\d+)', TemplateView.as_view(template_name="crowdfunding/ok.html"), name='crowdfunding-ok'),
    #re_path('pay/(?P<amount>\d+)', views2.process_payment, name="pay"),
]