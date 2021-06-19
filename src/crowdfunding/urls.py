from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework import routers
from crowdfunding.api.views import ProjectInvestmentViewSet
from crowdfunding.views import (
    stripe_checkout,
    ProjectInvestmentView,
    InvestViewBase,
    ProjectProgressView,
    create_checkout_session,
    stripe_checkout2,
    stripe_webhook,
)
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
    path('pay2/', stripe_checkout2, name="stripe-checkout2"),
    path(
        'pay/stripe-cookies-failure/',
        TemplateView.as_view(
            template_name="crowdfunding/stripe_cookies_failure.html"
        )
    ),
    #path('payment-done/', payment_done, name='payment_done'),
    #path('payment-cancelled/', payment_canceled, name='payment_cancelled'),
    path('fund/', ProjectInvestmentView.as_view(), name="fund"),
    path('progress/', ProjectProgressView.as_view(), name='progress'),
    #path('stripe/', include("djstripe.urls", namespace="djstripe")),
    #re_path('checkouts/', create_checkout, name="create-checkout"),
    #re_path('ok/(?P<amount>\d+)', TemplateView.as_view(template_name="crowdfunding/ok.html"), name='crowdfunding-ok'),
    path(
        'success/',
        TemplateView.as_view(
            template_name="crowdfunding/stripe_charge_success.html"
        ),
        name="success"
    ),
    path(
        'cancel/',
        TemplateView.as_view(
            template_name="crowdfunding/stripe_charge_cancel.html"
        ),
        name="cancel"
    ),
    path(
        'create-checkout-session/',
        create_checkout_session,
        name="create-checkout-session",
    ),
    path(
        'stripe-webhook/',
        stripe_webhook,
        name="stripe-webhook",
    ),
]