from django import forms
from django.conf import settings
from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from discourse.models import AccessControl
from invitations.utils import get_invitation_model
from invitations.forms import CleanEmailMixin

Invitation = get_invitation_model()


class InviteForm(forms.Form, CleanEmailMixin):
    """
    Form used by verified users to send invitations to their contacts
    using the invitee's email address
    """
    def __init__(self, *args, **kwargs):
        super(InviteForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'invite-form'
        self.helper.form_class = 'blueForms'
        self.helper.form_action = 'invite:send-invite'
        #self.helper.form_group_wrapper_class = 'row'
        #self.helper.label_class = 'offset-md-1 col-md-1'
        #self.helper.field_class = 'col-md-8'
        self.helper.add_input(Submit('submit', _('Submit')))
        self.helper.form_method = 'post'
    
    CATEGORY_CHOICES = AccessControl.objects.filter(authorize=True).values_list('category__name', 'category__label')
        
    email = forms.CharField(
        label=_('Email'),
        max_length=254,
    )
    category = forms.ChoiceField(
        label=_('Please choose a category for the invitee'),
        choices=CATEGORY_CHOICES,
    )
    certify = forms.BooleanField(
        label=_("I hereby certify that the person I am inviting do belong to this category.")    
    )

    def save(self, email, category):
        return Invitation.create(
            email=email,
            category=category
        )