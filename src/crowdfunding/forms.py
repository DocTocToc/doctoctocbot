from django import forms
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _
from .models import ProjectInvestor

class CrowdfundingHomeForm(forms.Form):
    custom_amount = forms.IntegerField(
        label='Custom amount',
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
    
class CrowdfundingCompleteForm(ModelForm):
    class Meta:
        model = ProjectInvestor
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