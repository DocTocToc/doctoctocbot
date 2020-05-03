from django.urls import include, path
from django_registration.backends.activation.views import RegistrationView
from django.views.generic import TemplateView

from registration.views import OneStepRegistrationView
from registration.forms import RegistrationFormPasswordless, RegistrationFormPasswordlessCaseInsensitiveSocial
from registration.forms import RegistrationFormInviteEmail


#app_name = 'registration'

urlpatterns = [
    path(
        'accounts/activate/complete/',
        TemplateView.as_view(
            template_name='django_registration/activation_complete.html'
        ),
        name='django_registration_activation_complete',
    ),
    path('accounts/',
        include('django_registration.backends.activation.urls')
    ),

    path('accounts/register/',
        RegistrationView.as_view(
            form_class=RegistrationFormPasswordless
        ),
        name='django_registration_register',
    ),
    path('accounts/register/invite/email/',
        OneStepRegistrationView.as_view(form_class= RegistrationFormInviteEmail),
        name='register-invite-email',
    ),
    path('accounts/registersocial/',
        RegistrationView.as_view(
            form_class=RegistrationFormPasswordlessCaseInsensitiveSocial
        ),
        name='django_registration_register_social',
    ),
    path('accounts/',
        include('django_registration.backends.one_step.urls')
    ),
    path('accounts/register/disallowed/',
         TemplateView.as_view(
             template_name='django_registration/registration_disallowed.html'
             ),
         name='registration_disallowed'
    ),

]