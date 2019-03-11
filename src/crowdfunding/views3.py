from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse

from .constants import TRANSACTION_SUCCESS_STATUSES
from .gateway import generate_client_token, transact, find_transaction


def index(request):
    return redirect('crowdfunding:new-checkout')

def new_checkout(request):
    client_token = generate_client_token()
    context = {'client_token': client_token}
    return render(request, 'crowdfunding/checkouts/new.html', context)

def show_checkout(request, transaction_id):
    transaction = find_transaction(transaction_id)
    result = {}
    if transaction.status in TRANSACTION_SUCCESS_STATUSES:
        result = {
            'header': 'Sweet Success!',
            'icon': 'success',
            'message': 'Your test transaction has been successfully processed. See the Braintree API response and try again.'
        }
    else:
        result = {
            'header': 'Transaction Failed',
            'icon': 'fail',
            'message': 'Your test transaction has a status of ' + transaction.status + '. See the Braintree API response and try again.'
        }
    context = {'transaction': transaction, 'result': result}
    return render(request, 'crowdfunding/checkouts/show.html', context)

def create_checkout(request):
    form = request.POST
    result = transact({
        'amount': form['amount'],
        'payment_method_nonce': form['payment_method_nonce'],
        'options': {
            "submit_for_settlement": True
        }
    })

    if result.is_success or result.transaction:
        return redirect('crowdfunding:show-checkout', result.transaction.id )
    else:
        for x in result.errors.deep_errors: messages.error(request, 'Error: %s: %s' % (x.code, x.message))
        return redirect('crowdfunding:new-checkout')
    
"""
class CheckoutView(generic.FormView):
    #This view lets the user initiate a payment.
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
        
        #Create a new transaction and submit it.
        #I don't gather the whole address in this example, but I can
        #highly recommend to do that. It will help you to avoid any
        #fraud issues, since some providers require matching addresses
         

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
"""