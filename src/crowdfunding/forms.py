from django.contrib.auth.validators import ASCIIUsernameValidator
from django import forms
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from .models import ProjectInvestment
from registration.forms import RegistrationFormPasswordlessCaseInsensitiveSocial as RegistrationForm

class UserNameField(forms.CharField):
    default_validators = [ASCIIUsernameValidator]


class CrowdfundingHomeTwitterForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(CrowdfundingHomeTwitterForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'crowdfunding-form'
        # self.helper.form_class = 'form-horizontal'
        self.helper.form_method = 'post'
        self.helper.form_action = '/crowdfunding/home/'
        self.helper.form_group_wrapper_class = 'row'
        # self.helper.label_class = 'offset-md-1 col-md-1'
        self.helper.label_class = 'col-md-8'
        self.helper.field_class = 'col-md-8'
        self.helper.add_input(Submit('submit', 'Submit'))

    def clean(self):
        cleaned_data = super().clean()
        
        #email = cleaned_data.get("email")
        #invoice = cleaned_data.get("invoice")

        #if invoice and not email:
        #    msg = "We need your email to send your invoice."
        #    self.add_error('email', msg)

    def save(self):
        pass

    custom_amount = forms.IntegerField(
        label=_('Custom amount'),
        max_value=1000,
        min_value=1,
        required=False
    )

    preset_amount = forms.IntegerField(
        label='Preset amount',
        widget=forms.HiddenInput(),
        max_value=1000,
        min_value=1,
        required=False
    )

    username = UserNameField(
        label=_('Username')
    )
    #invoice = forms.TypedChoiceField(
    #    label=_('Do you want an invoice?'),
    #    coerce=lambda x: x =='True', 
    #    choices=((True, 'Yes'), (False, 'No')),
    #    required=False,
    #)
    
    email = forms.EmailField(
        label=_('Email'),
        required=False
    )
    public = forms.TypedChoiceField(
        label=_('Do you want to appear on the donor list?'),
        coerce=lambda x: x == 'True',
        choices=((True, 'Yes'), (False, 'No')),
        required=False,
    )


class CrowdfundingHomeDjangoUserForm(RegistrationForm):
    custom_amount = forms.IntegerField(
        label=_('Custom amount'),
        max_value=1000,
        min_value=1,
        required=False)

    preset_amount = forms.IntegerField(
        label='Preset amount',
        widget=forms.HiddenInput(),
        max_value=1000,
        min_value=1,
        required=False
    )

    public = forms.TypedChoiceField(
        label=_('Do you want to appear on the donor list?'),
        coerce=lambda x: x == 'True',
        choices=((True, 'Yes'), (False, 'No')),
        required=False,
    )


class CrowdfundingCompleteForm(ModelForm):

    class Meta:
        model = ProjectInvestment
        fields = ['pledged']


class CheckoutForm(forms.Form):
    payment_method_nonce = forms.CharField(
        max_length=1000,
        widget=forms.widgets.HiddenInput,
        required=False,
    )

    def clean(self):
        self.cleaned_data = super(CheckoutForm, self).clean()
        # Braintree nonce is missing
        if not self.cleaned_data.get('payment_method_nonce'):
            raise forms.ValidationError(_(
                'We couldn\'t verify your payment. Please try again.'))
        return self.cleaned_data

