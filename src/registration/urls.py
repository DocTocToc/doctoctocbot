from django.urls import include, path
from django_registration.backends.activation.views import RegistrationView
from registration.views import OneStepRegistrationView

from registration.forms import RegistrationFormPasswordless, RegistrationFormPasswordlessCaseInsensitiveSocial

from registration.forms import RegistrationFormInviteEmail


app_name = 'registration'

urlpatterns = [
    path('accounts/register/',
        RegistrationView.as_view(
            form_class=RegistrationFormPasswordless
        ),
        name='django_registration_register',
    ),
    path('accounts/register/invite/email/',
        OneStepRegistrationView.as_view(form_class= RegistrationFormInviteEmail),
        name='django_registration_register_invite_email',
    ),
    path('accounts/registersocial/',
        RegistrationView.as_view(
            form_class=RegistrationFormPasswordlessCaseInsensitiveSocial
        ),
        name='django_registration_register_social',
    ),
    path('accounts/',
        include('django_registration.backends.activation.urls')
    ),
    path('accounts/',
        include('django_registration.backends.one_step.urls')
    ),
]