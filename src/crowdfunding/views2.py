from decimal import *
import logging

from django.core import signing
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views import generic, View
from django.views.decorators.csrf import csrf_exempt
from random import randint
from django.views.generic.edit import FormView
from django.views.generic import ListView
from django.db.models import Count
from django.contrib.auth import get_user_model
from django.core.exceptions import SuspiciousOperation
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string

import braintree
from paypal.standard.forms import PayPalPaymentsForm
#from django_registration.views import RegistrationView
from django_registration.views import RegistrationView as BaseRegistrationView
from django_registration import signals

from .constants import ITEM_NAME
from .forms import CrowdfundingHomeTwitterForm, CrowdfundingHomeDjangoUserForm, CheckoutForm
from .models import Project, ProjectInvestment, Tier

logger = logging.getLogger(__name__)

REGISTRATION_SALT = getattr(settings, 'REGISTRATION_SALT', 'registration')

def get_amount(form): 
    custom_amount = form.cleaned_data.get('custom_amount')
    preset_amount = form.cleaned_data.get('preset_amount')
    return custom_amount or preset_amount


class InvestViewDjango(BaseRegistrationView):
    email_body_template = 'django_registration/activation_email_body.txt'
    email_subject_template = 'django_registration/activation_email_subject.txt'
    
    def get_success_url(self, _):
        return reverse_lazy(
            'crowdfunding:pay',
            current_app='crowdfunding')

    def _form_valid(self, form):
        pi = ProjectInvestment()
        
        amount = get_amount(form)
        pi.pledged = amount
        self.request.session['amount'] = amount
                
        username = form.cleaned_data.get('username')
        pi.name = username
        self.request.session['username'] = username
        
        #invoice = form.cleaned_data.get('invoice')
        #self.request.session['invoice'] = invoice
        
        email = form.cleaned_data.get('email')
        self.request.session['email'] = email
        pi.email = email
        
        public = form.cleaned_data.get('public')
        self.request.session['public'] = public
        pi.public = public
        
        User = get_user_model()
        
        try: 
            pi.user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise SuspiciousOperation("Invalid request; see documentation for correct paramaters")

        pi.project = Project.objects.get(name=settings.PROJECT_NAME)        
        pi.save()
        self.request.session['custom'] = str(pi.id)
        return
    
    def get_form_class(self):
        return CrowdfundingHomeDjangoUserForm
    
    def get_form(self):
        form = super(InvestViewDjango, self).get_form(self.get_form_class())
        return form
    
    def get_template_names(self):
        return 'crowdfunding/home_django.html'
    
    def register(self, form):
        new_user = self.create_inactive_user(form)
        signals.user_registered.send(
            sender=self.__class__,
            user=new_user,
            request=self.request
        )
        self._form_valid(form)
        return new_user

    def create_inactive_user(self, form):
        """
        Create the inactive user account and send an email containing
        activation instructions.
        """
        new_user = form.save(commit=False)
        new_user.is_active = False
        new_user.save()

        self.send_activation_email(new_user)

        return new_user

    def get_activation_key(self, user):
        """
        Generate the activation key which will be emailed to the user.
        """
        return signing.dumps(
            obj=user.get_username(),
            salt=REGISTRATION_SALT
        )

    def get_email_context(self, activation_key):
        """
        Build the template context used for the activation email.
        """
        scheme = 'https' if self.request.is_secure() else 'http'
        return {
            'scheme': scheme,
            'activation_key': activation_key,
            'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
            'site': get_current_site(self.request)
        }

    def send_activation_email(self, user):
        """
        Send the activation email. The activation key is the username,
        signed using TimestampSigner.
        """
        activation_key = self.get_activation_key(user)
        context = self.get_email_context(activation_key)
        context['user'] = user
        subject = render_to_string(
            template_name=self.email_subject_template,
            context=context,
            request=self.request
        )
        # Force subject to a single line to avoid header-injection
        # issues.
        subject = ''.join(subject.splitlines())
        message = render_to_string(
            template_name=self.email_body_template,
            context=context,
            request=self.request
        )
        user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)



class InvestViewTwitter(FormView):  
    def get_success_url(self):
        return reverse_lazy(
            'crowdfunding:pay',
            current_app='crowdfunding')
        
    def form_valid(self, form):
        if form.cleaned_data.get('email') and not self.request.user.email:
            #logger.debug('email: %s' %form.cleaned_data.get('email'))
            self.request.user.email = form.cleaned_data.get('email')
            self.request.user.save()

        pi = ProjectInvestment()
        
        amount = get_amount(form)
        pi.pledged = amount
        self.request.session['amount'] = amount
                
        username = form.cleaned_data.get('username')
        pi.name = username
        self.request.session['username'] = username
        
        #invoice = form.cleaned_data.get('invoice')
        #self.request.session['invoice'] = invoice
        
        email = form.cleaned_data.get('email')
        self.request.session['email'] = email
        pi.email = email
        
        public = form.cleaned_data.get('public')
        self.request.session['public'] = public
        pi.public = public
        pi.user = self.request.user
        pi.project = Project.objects.get(name=settings.PROJECT_NAME)
        pi.save()
        self.request.session['custom'] = str(pi.id)
        return super().form_valid(form)

    def get_initial(self, *args, **kwargs):
        username = self.request.user.username
        email = self.request.user.email
        data = {
            'username': username,
            'email': email
        }
        return data
    
    def get_form_class(self):
        return CrowdfundingHomeTwitterForm
    
    def get_form(self):
        form = super(InvestViewTwitter, self).get_form(self.get_form_class())
        form.fields['username'].widget.attrs['readonly'] = 'readonly'
        return form

    def get_template_names(self):
        return 'crowdfunding/home_twitter.html'



class InvestViewBase(View):
    def is_twitter_auth(self):
        if not self.request.user.is_authenticated:
            return False
        return bool(self.request.user.social_auth.filter(provider='twitter'))
    
    def get(self, *args, **kwargs):
        if self.is_twitter_auth():
            return InvestViewTwitter.as_view()(self.request)
            #return InvestViewTwitter().get(self, *args, **kwargs)
        else:
            return InvestViewDjango.as_view()(self.request)
    
    def get_success_url(self):
        return reverse_lazy(
            'crowdfunding:pay',
            current_app='crowdfunding')

    def form_valid(self, form):
        if self.is_twitter_auth():
            return InvestViewTwitter().form_valid(form)
        else:
            return InvestViewDjango().form_valid(form)

    def post(self, request, *args, **kwargs):
        if self.is_twitter_auth():
            return InvestViewTwitter.as_view()(self.request)
            #return InvestViewTwitter().post(self, request, *args, **kwargs)
        else:
            return InvestViewDjango.as_view()(self.request)
    
    #def get_initial(self, *args, **kwargs):
    #    if self.is_twitter_auth():
    #        return InvestViewTwitter().get_initial(self, *args, **kwargs)
    #    else:
    #        return

    def get_form_class(self):
        if self.is_twitter_auth():
            return InvestViewTwitter().get_form_class(self)
        else:
            return InvestViewDjango().get_form_class(self)
        
    def get_form_class(self):
        if self.is_twitter_auth():
            return InvestViewTwitter().get_form(self)
        else:
            return InvestViewDjango().get_form(self)
        
    def get_template_names(self):
        if self.is_twitter_auth():
            return InvestViewTwitter().get_template_names(self)
        else:
            return InvestViewDjango().get_template_names(self)

class InvestView(FormView):

    # replaced by get_template_names()
    #template_name = 'crowdfunding/home_twitter.html'
    
    #if _is_twitter_auth():
    #else:
    #    form_class = CrowdfundingHomeForm  
    def get_success_url(self):
        return reverse_lazy(
            'crowdfunding:pay',
            current_app='crowdfunding')
    
    def is_twitter_auth(self):
        if not self.request.user.is_authenticated:
            return False
        return bool(self.request.user.social_auth.filter(provider='twitter'))

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            if self.is_twitter_auth():
                logger.debug('user is using Twitter Account!')
                logger.debug('user.email: %s' % self.request.user.email)
                if form.cleaned_data.get('email') and not self.request.user.email:
                    logger.debug('email: %s' %form.cleaned_data.get('email'))
                    self.request.user.email = form.cleaned_data.get('email')
                    self.request.user.save()
            else:
                logger.debug('user is using Django default authentication or another social provider')
        else:
                pass
                # create user here
                # validate against known twitter usernames to prevent impersonation
        pi = ProjectInvestment()
        
        amount = self.get_amount(form)
        pi.pledged = amount
        self.request.session['amount'] = amount
                
        username = form.cleaned_data.get('username')
        pi.name = username
        self.request.session['username'] = username
        
        #invoice = form.cleaned_data.get('invoice')
        #self.request.session['invoice'] = invoice
        
        email = form.cleaned_data.get('email')
        self.request.session['email'] = email
        pi.email = email
        
        public = form.cleaned_data.get('public')
        self.request.session['public'] = public
        pi.public = public
        
        if self.request.user.is_authenticated:
            pi.user = self.request.user
        else:
            User = get_user_model()
            try:
                pi.user = User.objects.get(username=username)
            except User.DoesNotExist:
                raise SuspiciousOperation("Invalid request; see documentation for correct paramaters")
                
        pi.project = Project.objects.get(name=settings.PROJECT_NAME)
        
        pi.save()
        
        self.request.session['custom'] = str(pi.id)
        
        return super().form_valid(form)
        
    def get_amount(self, form): 
        custom_amount = form.cleaned_data.get('custom_amount')
        preset_amount = form.cleaned_data.get('preset_amount')
        return custom_amount or preset_amount
            
    def post(self, request, *args, **kwargs):
        form = self.get_form()
        return super().post(request, *args, **kwargs)
    
    def get_initial(self):
        username = None
        email = None
        if self.request.user.is_authenticated:
            username = self.request.user.username
            email = self.request.user.email

        data = {
            'username': username,
            'email': email
        }
        return data
    
    def get_form_class(self):
        if self.is_twitter_auth():
            return CrowdfundingHomeTwitterForm
        else:
            return CrowdfundingHomeDjangoUserForm
    
    def get_form(self):
        form = super(InvestView, self).get_form(self.get_form_class())
        if self.is_twitter_auth():
            form.fields['username'].widget.attrs['readonly'] = 'readonly'
        return form
    
    def get_template_names(self):
        if self.is_twitter_auth():
            return 'crowdfunding/home_twitter.html'
        else:
            return 'crowdfunding/home_django.html'
        

def process_payment(request):
    host = request.get_host()
    amount = request.session.get('amount', 0)
    amount_dec = Decimal(request.session.get('amount')).quantize(Decimal('.01'))
    paypal_dict = {
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        'amount': '%.2f' % amount_dec,
        'item_name': ITEM_NAME,
        'custom': request.session.get('custom'),
        'currency_code': 'EUR',
        'notify_url': 'http://{}{}'.format(host,
                                           reverse_lazy('crowdfunding:paypal-ipn')),
        'return_url': 'http://{}{}'.format(host,
                                           reverse_lazy('crowdfunding:payment_done')),
        'cancel_return': 'http://{}{}'.format(host,
                                              reverse_lazy('crowdfunding:payment_cancelled')),
    }
    
    form = PayPalPaymentsForm(initial=paypal_dict)
    return render(request, 'crowdfunding/pay.html', {'form': form, 'amount': amount})

@csrf_exempt
def payment_done(request):
    return render(request, 'crowdfunding/payment_done.html')
 
 
@csrf_exempt
def payment_canceled(request):
    return render(request, 'crowdfunding/payment_cancelled.html')


class ProjectInvestmentView(ListView):

    context_object_name = 'investment_list'
    queryset = ProjectInvestment.objects.all()
    template_name = 'crowdfunding/fund.html'
    
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        #context['book_list'] = Book.objects.all()
        tier_lst = []
        for t in Tier.objects.filter(project=Project.objects.get(name='doctoctocbot')):
            tier = {}
            tier['title']= t.title
            tier['emoji']= t.emoji
            tier['description']= t.description
            tier['funder_lst'] = list(ProjectInvestment.objects.
                                      filter(paid=True).
                                      filter(public=True).
                                      filter(pledged__gte=t.min, pledged__lte=t.max))
            tier_lst.append(tier)
        context['tier_lst'] = tier_lst
        context['investor_count'] = (ProjectInvestment
                                     .objects
                                     .filter(paid=True)
                                     .distinct('user')
                                     .count())   
        return context

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