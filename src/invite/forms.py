from django import forms
from django.utils.translation import ugettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from discourse.models import AccessControl


class InviteForm(forms.Form):
    """
    Form used by verified users to send invitations to their contacts
    using the invitee's email address
    """
    def __init__(self, *args, **kwargs):
        super(InviteForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'invite-form'
        self.helper.form_class = 'blueForms'
        self.helper.form_action = 'invite:form'
        #self.helper.form_group_wrapper_class = 'row'
        #self.helper.label_class = 'offset-md-1 col-md-1'
        #self.helper.field_class = 'col-md-8'
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.form_method = 'post'
    
    CATEGORY_CHOICES = AccessControl.objects.filter(authorize=True).values_list('category__name', 'category__label')
        
    email = forms.CharField(
        label=_('Email'),
        max_length=254,
    )
    category = forms.ChoiceField(
        choices=CATEGORY_CHOICES,
    )
    certify = forms.BooleanField(
        label=_("I hereby certify that the person I am inviting do belong to this category.")    
    )