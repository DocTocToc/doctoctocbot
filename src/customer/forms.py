from django import forms
from django.utils.translation import ugettext_lazy as _
from django_countries.fields import CountryField

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from customer.models import Customer
from bootstrap_modal_forms.forms import BSModalForm


class CustomerReadOnlyForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(CustomerReadOnlyForm, self).__init__(*args, **kwargs)
        try:
            customer = Customer.objects.get(user=self.user)
        except Customer.DoesNotExist:
            return
        self.helper = FormHelper()
        self.helper.form_id = 'customer-form'
        self.helper.form_class = 'form-horizontal'
        self.helper.form_method = 'post'
        self.helper.form_action = '/customer/'
        self.helper.form_group_wrapper_class = 'row'
        self.helper.label_class = 'offset-md-1 col-md-1'
        self.helper.field_class = 'col-md-8'
        self.fields['country'].label = _('Country')
        self.helper.add_input(Submit('submit', 'Submit'))
        self.fields['id'].initial=customer.id
        self.fields['first_name'].initial=customer.first_name
        self.fields['last_name'].initial=customer.last_name
        self.fields['company'].initial=customer.company
        self.fields['address_1'].initial=customer.address_1
        self.fields['address_2'].initial=customer.address_2
        self.fields['country'].initial=customer.country
        self.fields['email'].initial=customer.email
        self.fields['city'].initial=customer.city
        self.fields['state'].initial=customer.state
        self.fields['zip_code'].initial=customer.zip_code

    id = forms.CharField(
        disabled=True,
        widget=forms.HiddenInput(),
    )
    first_name = forms.CharField(
        label=_('First name'),
        max_length=128,
        disabled=True,
    )
    last_name = forms.CharField(
        label=_('Last name'),
        max_length=128,
        disabled=True,
    )
    company = forms.CharField(
        label=_('Company'),
        max_length=128,
        disabled=True,
    )
    address_1 = forms.CharField(
        label=_('Address'),
        max_length=128,
        disabled=True,
    )
    address_2 = forms.CharField(
        label=_('Address'),
        max_length=128,
        required=False,
        disabled=True,
    )
    country = CountryField(
        blank_label=_('(select country)')
    ).formfield(disabled=True,)
    phone = forms.CharField(
        label=_('Telephone'),
        max_length=32,
        required=False,
        disabled=True,
    )
    email = forms.CharField(
        label=_('Email'),
        max_length=254,
        disabled=True,
    )
    city = forms.CharField(
        label=_('City'),
        max_length=128,
        disabled=True,
    )
    state = forms.CharField(
        label=_('State'),
        max_length=128,
        required=False,
        disabled=True,
    )
    zip_code = forms.CharField(
        label=_('ZIP code'),
        max_length=32,
        disabled=True,
    )
"""
class CustomerForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(CustomerForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'customer-form'
        self.helper.form_class = 'form-horizontal'
        self.helper.form_method = 'post'
        self.helper.form_action = '/customer/'
        self.helper.form_group_wrapper_class = 'row'
        self.helper.label_class = 'offset-md-1 col-md-1'
        self.helper.field_class = 'col-md-8'
        self.fields['country'].label = _('Country')
        self.helper.add_input(Submit('submit', 'Submit'))

    first_name = forms.CharField(
        label=_('First name'),
        max_length=128
    )
    last_name = forms.CharField(
        label=_('Last name'),
        max_length=128
    )
    company = forms.CharField(
        label=_('Company'),
        max_length=128,
    )
    address_1 = forms.CharField(
        label=_('Address'),
        max_length=128
    )
    address_2 = forms.CharField(
        label=_('Address'),
        max_length=128,
        required=False
    )
    country = CountryField(
        blank_label=_('(select country)')
    ).formfield()
    phone = forms.CharField(
        label=_('Telephone'),
        max_length=32,
        required=False
    )
    email = forms.CharField(
        label=_('Email'),
        max_length=254
    )
    city = forms.CharField(
        label=_('City'),
        max_length=128
    )
    state = forms.CharField(
        label=_('State'),
        max_length=128,
        required=False
    )
    zip_code = forms.CharField(
        label=_('ZIP code'),
        max_length=32
    )
"""

class CustomerForm(BSModalForm):
    class Meta:
        model = Customer
        fields = [
            'first_name',
            'last_name',
            'company',
            'email',
            'address_1',
            'address_2',
            'country',
            'city',
            #'state',
            'zip_code',
        ]
