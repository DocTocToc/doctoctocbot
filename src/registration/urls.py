from django.conf.urls import include, url

from django_registration.backends.activation.views import RegistrationView

from registration.forms import RegistrationFormPasswordless


urlpatterns = [
    # ... other URL patterns here
    url(r'^accounts/register/$',
        RegistrationView.as_view(
            form_class=RegistrationFormPasswordless
        ),
        name='django_registration_register',
    ),
    url(r'^accounts/',
        include('django_registration.backends.activation.urls')
    ),
    # ... more URL patterns
]