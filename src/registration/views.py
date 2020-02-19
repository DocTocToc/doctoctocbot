import logging
from django_registration.backends.one_step.views import RegistrationView
from django.urls import reverse
from django.contrib.auth import authenticate, get_user_model, login
from django_registration import signals
from django.conf import settings
from invite.models import CategoryInvitation

logger=logging.getLogger(__name__)

User = get_user_model()

class OneStepRegistrationView(RegistrationView):
    success_url = "/user/profile/"
    disallowed_url = "/accounts/register/disallowed/"
    
    def register(self, form):
        # Check that the email used to register is identical to invitation email
        registration_email = form.cleaned_data["email"]
        key = self.request.session.get(settings.INVITATION_SESSION_KEY, None)
        try:
            invitation = CategoryInvitation.objects.get(key=key)
        except CategoryInvitation.DoesNotExist:
            return
        if registration_email != invitation.email:
            return
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

    def registration_allowed(self):
        """
        Override this to enable/disable user registration, either
        globally or on a per-request basis.
        """
        key = self.request.session.get(settings.INVITATION_SESSION_KEY, None)
        if not key:
            logger.debug("no key")
            return False
        logger.debug(f"key:{key}")
        return CategoryInvitation.objects.filter(key=key, accepted=True).exists()