from decimal import *
from random import randint

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

import braintree

from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import generic
from django.utils.translation import gettext as _

from paypal.standard.forms import PayPalPaymentsForm

from .forms import CrowdfundingHomeForm, CheckoutForm

def get_amount(request):
    if request.method == 'POST':
        form = CrowdfundingHomeForm(request.POST)
        if form.is_valid():
            custom_amount = form.cleaned_data.get('custom_amount')
            preset_amount = form.cleaned_data.get('preset_amount')
            amount = custom_amount or preset_amount
            """
            return HttpResponseRedirect(reverse('crowdfunding:crowdfunding-ok',
                                                kwargs={'amount': amount},
                                                current_app='crowdfunding'
                                                )
            )
            """
            return HttpResponseRedirect(reverse('crowdfunding:pay',
                                                kwargs={'amount': amount},
                                                current_app='crowdfunding'
                                                )
            )            
    else:
        form= CrowdfundingHomeForm()
        
    return (render(request, 'crowdfunding/home.html', {'form': form}))

def process_payment(request, amount):
    #amount = request.GET.get('amount', '0')
    host = request.get_host()
    html = "<!DOCTYPE html><html><body>Amount: %s. Host: %s </body></html>" % (amount, host)
    amount_dec = Decimal(amount).quantize(Decimal('.01'))
    paypal_dict = {
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        'amount': '%.2f' % amount_dec,
        'item_name': 'Développement outil professionnel en ligne doctoctoc.net',
        'invoice': str(randint(1,10000)),
        'currency_code': 'EUR',
        'notify_url': 'http://{}{}'.format(host,
                                           reverse('crowdfunding:paypal-ipn')),
        'return_url': 'http://{}{}'.format(host,
                                           reverse('crowdfunding:payment_done')),
        'cancel_return': 'http://{}{}'.format(host,
                                              reverse('crowdfunding:payment_cancelled')),
    }
 
    form = PayPalPaymentsForm(initial=paypal_dict)
    return render(request, 'crowdfunding/pay.html', {'form': form, 'amount': amount})
    return HttpResponse(html)

@csrf_exempt
def payment_done(request):
    return render(request, 'crowdfunding/payment_done.html')
 
 
@csrf_exempt
def payment_canceled(request):
    return render(request, 'crowdfunding/payment_cancelled.html')

class CheckoutView(generic.FormView):
    """This view lets the user initiate a payment."""
    form_class = CheckoutForm
    template_name = 'crowdfunding/checkout.html'
    
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        # We need the user to assign the transaction
        self.user = request.user
        # Ha! There it is. This allows you to switch the
        # Braintree environments by changing one setting

            
        # Configure Braintree (the new instance method)
        self.gateway = braintree.BraintreeGateway(
            braintree.Configuration(
            braintree_env,
            merchant_id=settings.BRAINTREE_MERCHANT_ID,
            public_key=settings.BRAINTREE_PUBLIC_KEY,
            private_key=settings.BRAINTREE_PRIVATE_KEY,
            )
        )
        
        # Generate a client token. We'll send this to the form to
        # finally generate the payment nonce
        # You're able to add something like ``{"customer_id": 'foo'}``,
        # if you've already saved the ID
        self.braintree_client_token = self.gateway.client_token.generate({})
        return super(CheckoutView, self).dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        ctx = super(CheckoutView, self).get_context_data(**kwargs)
        ctx.update({
            'braintree_client_token': self.braintree_client_token,
        })
        return ctx

    def form_valid(self, form):
        # Braintree customer info
        # You can, for sure, use several approaches to gather customer infos
        # For now, we'll simply use the given data of the user instance
        customer_kwargs = {
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "email": self.user.email,
        }
        
        # Create a new Braintree customer
        # In this example we always create new Braintree users
        # You can store and re-use Braintree's customer IDs, if you want to
        result = self.gateway.customer.create(customer_kwargs)
        if not result.is_success:
            # Ouch, something went wrong here
            # I recommend to send an error report to all admins
            # , including ``result.message`` and ``self.user.email``
            
            context = self.get_context_data()
            # We re-generate the form and display the relevant braintree error
            context.update({
                'form': self.get_form(self.get_form_class()),
                'braintree_error': u'{} {}'.format(
                    result.message, _('Please get in contact.'))
            })
            return self.render_to_response(context)
        
        # If the customer creation was successful you might want to also
        # add the customer id to your user profile
        customer_id = result.customer.id
        
        """
        Create a new transaction and submit it.
        I don't gather the whole address in this example, but I can
        highly recommend to do that. It will help you to avoid any
        fraud issues, since some providers require matching addresses
         
        """
        address_dict = {
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "street_address": 'street',
            "extended_address": 'street_2',
            "locality": 'city',
            "region": 'state_or_region',
            "postal_code": 'postal_code',
            "country_code_alpha2": 'alpha2_country_code',
            "country_code_alpha3": 'alpha3_country_code',
            "country_name": 'country',
            "country_code_numeric": 'numeric_country_code',
        }
        
        # You can use the form to calculate a total or add a static total amount
        # I'll use a static amount in this example
        try:
            amount = int(self.request.GET.get('amount'))
        except TypeError:
            amount = 0
        result = self.gateway.transaction.sale({
            "customer_id": customer_id,
            "amount": amount,
            "payment_method_nonce": form.cleaned_data['payment_method_nonce'],
            "descriptor": {
                # Definitely check out https://developers.braintreepayments.com/reference/general/validation-errors/all/python#descriptor
                "name": "COMPANY.*test",
            },
            "billing": address_dict,
            "shipping": address_dict,
            "options": {
                # Use this option to store the customer data, if successful
                'store_in_vault_on_success': True,
                # Use this option to directly settle the transaction
                # If you want to settle the transaction later, use ``False`` and later on
                # ``braintree.Transaction.submit_for_settlement("the_transaction_id")``
                'submit_for_settlement': True,
            },
        })
        if not result.is_success:
            # Card could've been declined or whatever
            # I recommend to send an error report to all admins
            # , including ``result.message`` and ``self.user.email``
            context = self.get_context_data()
            context.update({
                'form': self.get_form(self.get_form_class()),
                'braintree_error': _(
                    'Your payment could not be processed. Please check your'
                    ' input or use another payment method and try again.')
            })
            return self.render_to_response(context)
        
        # Finally there's the transaction ID
        # You definitely want to send it to your database
        transaction_id = result.transaction.id
        # Now you can send out confirmation emails or update your metrics
        # or do whatever makes you and your customers happy :)
        return super(CheckoutView, self).form_valid(form)
    
    def get_success_url(self):
        # Add your preferred success url
        return reverse('crowdfunding:payment_done')