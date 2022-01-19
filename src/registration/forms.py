"""
Forms and validation code for user registration.

Note that all of these forms assume your user model is similar in
structure to Django's default User class. If your user model is
significantly different, you may need to write your own form class;
see the documentation for notes on custom user models with
django-registration.

"""
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UsernameField
from django.utils.translation import ugettext_lazy as _

from django_registration import validators
from django_registration.forms import RegistrationForm
from registration.validators import (
    CaseInsensitiveReservedSocialUsername,
    no_at_sign,
)
from crispy_forms.helper import FormHelper

User = get_user_model()


class RegistrationFormInviteEmail(RegistrationForm):
    """
    A form that creates a user, with no privileges, from the given username
    and password, following an invite.
    """
    email = forms.Field(
        widget=forms.EmailInput(attrs={'class':'form-control'}),
        label=_("Email (Be sure to use the same email to which the invitation was sent)")
    )
    
    class Meta(RegistrationForm.Meta):
        model = User
        fields = ("username", "password1", "password2", "email",)
        field_classes = {
            'username': UsernameField,
        }
        
    def __init__(self, *args, **kwargs):
        super(RegistrationFormInviteEmail, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'blueForms'
        self.fields[User.USERNAME_FIELD].validators.extend(
            [validators.CaseInsensitiveUnique(
                User, User.USERNAME_FIELD,
                validators.DUPLICATE_USERNAME
                ),
            CaseInsensitiveReservedSocialUsername]
        )
        email_field = User.get_email_field_name()
        self.fields[email_field].validators.append(
            validators.CaseInsensitiveUnique(
                User, email_field,
                validators.DUPLICATE_EMAIL
            )
        )


class UserCreationForm(forms.ModelForm):
    """
    A form that creates a user, with no privileges, from the given username.
    """

    class Meta:
        model = User
        fields = ("username",)
        field_classes = {'username': UsernameField}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self._meta.model.USERNAME_FIELD in self.fields:
            self.fields[self._meta.model.USERNAME_FIELD].widget.attrs.update({'autofocus': True})

    def save(self, commit=True):
        user = super().save(commit=False)
        password = User.objects.make_random_password(length=20)
        user.set_password(password)
        if commit:
            user.save()
        return user


class RegistrationFormPasswordless(UserCreationForm):
    """
    Form for registering a new user account.

    Validates that the requested username is not already in use, and
    requires the password to be entered twice to catch typos.

    Subclasses should feel free to add any additional validation they
    need, but should take care when overriding ``save()`` to respect
    the ``commit=False`` argument, as several registration workflows
    will make use of it to create inactive user accounts.

    """
    class Meta(UserCreationForm.Meta):
        fields = [
            User.USERNAME_FIELD,
            User.get_email_field_name(),
        ]

    error_css_class = 'error'
    required_css_class = 'required'

    def __init__(self, *args, **kwargs):
        super(RegistrationFormPasswordless, self).__init__(*args, **kwargs)
        email_field = User.get_email_field_name()
        if hasattr(self, 'reserved_names'):
            reserved_names = self.reserved_names
        else:
            reserved_names = validators.DEFAULT_RESERVED_NAMES
        username_validators = [
            validators.ReservedNameValidator(reserved_names),
            validators.validate_confusables
        ]
        self.fields[User.USERNAME_FIELD].validators.extend(username_validators)
        self.fields[email_field].validators.append(
            validators.validate_confusables_email
        )
        self.fields[email_field].required = True


class RegistrationFormPasswordlessCaseInsensitive(RegistrationFormPasswordless):
    """T

    Subclass of ``RegistrationForm`` enforcing case-insensitive
    uniqueness of usernames.

    """
    def __init__(self, *args, **kwargs):
        super(RegistrationFormPasswordlessCaseInsensitive, self).__init__(*args, **kwargs)
        self.fields[User.USERNAME_FIELD].validators.append(
            validators.CaseInsensitiveUnique(
                User, User.USERNAME_FIELD,
                validators.DUPLICATE_USERNAME
            )
        )


class RegistrationFormPasswordlessTermsOfService(RegistrationFormPasswordless):
    """
    Subclass of ``RegistrationForm`` which adds a required checkbox
    for agreeing to a site's Terms of Service.

    """
    tos = forms.BooleanField(
        widget=forms.CheckboxInput,
        label=_(u'I have read and agree to the Terms of Service'),
        error_messages={
            'required': validators.TOS_REQUIRED,
        }
    )


class RegistrationFormPasswordlessUniqueEmail(RegistrationFormPasswordless):
    """
    Subclass of ``RegistrationForm`` which enforces uniqueness of
    email addresses.

    """
    def __init__(self, *args, **kwargs):
        super(RegistrationFormPasswordlessUniqueEmail, self).__init__(*args, **kwargs)
        email_field = User.get_email_field_name()
        self.fields[email_field].validators.append(
            validators.CaseInsensitiveUnique(
                User, email_field,
                validators.DUPLICATE_EMAIL
            )
        )

class RegistrationFormPasswordlessCaseInsensitiveSocial(RegistrationFormPasswordless):
    """T

    Subclass of ``RegistrationForm`` enforcing case-insensitive
    uniqueness of usernames and adding social usernames (screen_name for Twitter)
    to reserved names.

    """
    def __init__(self, *args, **kwargs):
        super(RegistrationFormPasswordlessCaseInsensitiveSocial, self).__init__(*args, **kwargs)
        self.fields[User.USERNAME_FIELD].validators.extend(
            [
                validators.CaseInsensitiveUnique(
                User,
                User.USERNAME_FIELD,
                validators.DUPLICATE_USERNAME
                ),
                CaseInsensitiveReservedSocialUsername,
                no_at_sign,
            ]
        )