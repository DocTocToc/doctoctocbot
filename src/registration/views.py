from django_registration.backends.one_step.views import RegistrationView
from django.urls import reverse
from django.contrib.auth import authenticate, get_user_model, login
from django_registration import signals

User = get_user_model()

class OneStepRegistrationView(RegistrationView):
    success_url = "/user/profile/"
    
    def register(self, form):
        new_user = form.save()
        new_user = authenticate(
            **{
                User.USERNAME_FIELD: new_user.get_username(),
                "password": form.cleaned_data["password1"],
            }
        )
        login(self.request, new_user)
        signals.user_registered.send(
            sender=self.__class__, user=new_user, request=self.request
        )
        return new_user
