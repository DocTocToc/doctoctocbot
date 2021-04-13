from django.urls import path
from django.views.decorators.cache import cache_page
from display.views import All
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.views.generic import RedirectView

from landing import views

app_name = 'landing'

urlpatterns = [
    #path('', All.as_view(), name='index'),
    path('', TemplateView.as_view(template_name='display/home.html'), name='index'),
    path('user/', RedirectView.as_view(
        url='/user/profile/',
        permanent=True
        )
    ),
    path('user/profile/', login_required(views.UserProfile.as_view()), name='user'),
    path('user/social/', login_required(TemplateView.as_view(template_name="landing/user/social.html")), name="user-social"),
    path('user/contact/', login_required(TemplateView.as_view(template_name="landing/user/contact.html")), name="user-contact"),
    path('user/billing/', login_required(views.CustomerReadOnlyFormView), name="user-billing"),
    path('user/option/', login_required(TemplateView.as_view(template_name="landing/user/option.html")), name="user-option"),
    path('user/moderation', login_required(TemplateView.as_view(template_name="landing/user/moderation.html")), name="user-moderation"),
    path('user/contact/update/<uuid:pk>/', views.CustomerUpdateView.as_view(), name='update-customer'),
    path('user/account/', login_required(TemplateView.as_view(template_name="landing/user/account.html")), name='user-account'),
    path('status/<int:statusid>/', views.status),
    path('privacy/', TemplateView.as_view(template_name='landing/privacy/index.html'), name='privacy'),
    path('about/', TemplateView.as_view(template_name='landing/about/index.html'), name='about'),
    path('license/', TemplateView.as_view(template_name='landing/license/index.html'), name='license'),
    path('rules/', TemplateView.as_view(template_name='landing/rules/index.html'), name='rules'),
    path('values/', TemplateView.as_view(template_name='landing/values/index.html'), name='values'),
    path('follow/', TemplateView.as_view(template_name='landing/follow/index.html'), name='follow'),
    path('guidelines/', TemplateView.as_view(template_name='landing/guidelines/index.html'), name='guidelines'),
    path('moderation/', TemplateView.as_view(template_name='landing/moderation/index.html'), name='moderation'),
    path('moderation/moderator', TemplateView.as_view(template_name='landing/moderator/index.html'), name='moderator'),
    path('faq/', TemplateView.as_view(template_name='landing/faq/index.html'), name='faq'),
    path('spamtoctoc/', TemplateView.as_view(template_name='landing/spamtoctoc/index.html'), name='spamtoctoc'),
    path('categories/', TemplateView.as_view(template_name='landing/categories/index.html'), name='categories'),
    path('antiracism/', TemplateView.as_view(template_name='landing/antiracism/index.html'), name='antiracism'),




]
