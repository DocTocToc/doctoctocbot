from decimal import *
from uuid import UUID

from django.core import signing
from django.conf import settings
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import FormView
from django.views.generic import ListView
from django.contrib.auth import get_user_model
from django.core.exceptions import SuspiciousOperation
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.db import DatabaseError

import stripe
#from paypal.standard.forms import PayPalPaymentsForm
#from paypal.standard.forms import PayPalEncryptedPaymentsForm
#from paypal.standard.forms import PayPalSharedSecretEncryptedPaymentsForm
#from django_registration.views import RegistrationView
from django_registration.views import RegistrationView as BaseRegistrationView
from django_registration import signals

from .constants import ITEM_NAME, HOURLY_RATE_EUR
from .forms import CrowdfundingHomeAuthenticatedForm, CrowdfundingHomeDjangoUserForm
from .models import ProjectInvestment, Tier
from .tasks import handle_tweet_investment
from crowdfunding.project import get_project

import logging
logger = logging.getLogger(__name__)

REGISTRATION_SALT = getattr(settings, 'REGISTRATION_SALT', 'registration')

stripe.api_key = settings.STRIPE_SECRET_KEY

def get_amount(form): 
    custom_amount = form.cleaned_data.get('custom_amount')
    preset_amount = form.cleaned_data.get('preset_amount')
    return custom_amount or preset_amount


class InvestViewDjango(BaseRegistrationView):
    email_body_template = 'django_registration/activation_email_body.txt'
    email_subject_template = 'django_registration/activation_email_subject.txt'
    
    def get_success_url(self, _):
        return reverse_lazy(
            'crowdfunding:stripe-checkout',
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

        pi.project = get_project(self.request)        
        try:
            pi.save()
        except DatabaseError:
            return
        self.request.session['custom'] = str(pi.uuid)
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
        self.request.session['userid'] = new_user.id
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



class InvestViewAuthenticated(FormView):  
    def get_success_url(self):
        return reverse_lazy(
            'crowdfunding:stripe-checkout',
            current_app='crowdfunding')
        
    def form_valid(self, form):
        if form.cleaned_data.get('email') and not self.request.user.email:
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
        pi.project = get_project(self.request)
        try:
            pi.save()
        except DatabaseError:
            return
        self.request.session['custom'] = str(pi.uuid)
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
        return CrowdfundingHomeAuthenticatedForm
    
    def get_form(self):
        form = super(InvestViewAuthenticated, self).get_form(self.get_form_class())
        form.fields['username'].widget.attrs['readonly'] = 'readonly'
        return form

    def get_template_names(self):
        return 'crowdfunding/home_authenticated.html'



class InvestViewBase(View):
    def is_twitter_auth(self):
        if not self.request.user.is_authenticated:
            return False
        return bool(self.request.user.social_auth.filter(provider='twitter'))
    
    def get(self, *args, **kwargs):
        self.request.session.set_test_cookie()
        
        if self.request.user.is_authenticated:
            return InvestViewAuthenticated.as_view()(self.request)
        else:
            return InvestViewDjango.as_view()(self.request)
    
    def get_success_url(self):
        return reverse_lazy(
            'crowdfunding:stripe-checkout',
            current_app='crowdfunding')

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            return InvestViewAuthenticated().form_valid(form)
        else:
            return InvestViewDjango().form_valid(form)

    def post(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return InvestViewAuthenticated.as_view()(self.request)
        else:
            return InvestViewDjango.as_view()(self.request)
    
    def get_form_class(self):
        if self.request.user.is_authenticated:
            return InvestViewAuthenticated().get_form_class(self)
        else:
            return InvestViewDjango().get_form_class(self)
        
    def get_template_names(self):
        if self.request.user.is_authenticated:
            return InvestViewAuthenticated().get_template_names(self)
        else:
            return InvestViewDjango().get_template_names(self)

"""
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
    #form = PayPalSharedSecretEncryptedPaymentsForm(initial=paypal_dict)
    #form = PayPalEncryptedPaymentsForm(initial=paypal_dict)
    return render(request, 'crowdfunding/pay.html', {'form': form, 'amount': amount})
"""

def stripe_checkout(request):
    if request.session.test_cookie_worked():
        request.session.delete_test_cookie()
        amount_int = request.session.get('amount')
        amount_dec = Decimal(amount_int).quantize(Decimal('.01'))
        amount_str = "{:.2f}".format(amount_dec)
        amount_cents = amount_int * 100
        button_label = _("Pay with card")
        public_key = settings.STRIPE_PUBLIC_KEY
        return render(
            request,
            'crowdfunding/stripe_checkout.html',
            {'amount_str': amount_str,
             'public_key': public_key,
             'amount_cents': amount_cents,
             'button_label': button_label}
        )
    else:
        return render(
            request,
            'crowdfunding/stripe_cookies_failure.html',
        )


def charge(request):
    def render_error(request, frontend_error_msg):
        return render(
            request,
            "crowdfunding/stripe_charge_failure.html",
            {'frontend_error_msg': frontend_error_msg}
        )
     
    if request.method == 'POST':
        amount_int = request.session.get('amount', 0)
        amount_cents = amount_int * 100
        uuid_str = request.session.get('custom')
        userid = request.session.get('userid')
        
        try:
            UUID(uuid_str, version=4)
        except ValueError:
            err_str = _("UUID verification error.")
            logger.error(err_str)
            return render_error(
                request,
                err_str
            )
               
        try:
            charge = stripe.Charge.create(
                amount=amount_cents,
                currency='eur',
                description=ITEM_NAME,
                source=request.POST['stripeToken'],
                metadata={'uuid': uuid_str},
            )
            # mark project investment object as paid
            
        except stripe.error.CardError as e:
            # Since it's a decline, stripe.error.CardError will be caught
            body = e.json_body
            err  = body.get('error', {})
            err_msg=(
                "Status is: {}" 
                "Type is: {}"
                "Code is: {}" 
                "Param is: {}" 
                "Message is: {}" 
                .format(
                    e.http_status,
                    err.get('type'),
                    err.get('code'),
                    err.get('param'),
                    err.get('message')
                )
            )
            logger.error(err_msg)
            frontend_error_msg =(
                _("You payment card was not authorized."
                  "Pleace try again with this card or another. {}")
                .format(err.get('message')))
            return render_error(
                request,
                frontend_error_msg
            )
        
        except stripe.error.RateLimitError as e:
            err_str = _("Too many requests made to the API too quickly")
            logger.info(err_str)
            return render_error(
                request,
                err_str
            )
        
        except stripe.error.InvalidRequestError as e:
            err_str = _("Invalid parameters were supplied to Stripe's API")
            logger.error(err_str)
            return render_error(
                request,
                err_str
            )
        
        except stripe.error.AuthenticationError as e:
            err_str = _(
                "Authentication with Stripe's API failed"
                "(maybe you changed API keys recently)"
            )
            logger.info(err_str)
            return render_error(
                request,
                err_str
            )
        
        except stripe.error.APIConnectionError as e:
            err_str = _("Network communication with Stripe failed")
            logger.error(err_str)
            return render_error(
                request,
                err_str
            )
                    
        except stripe.error.StripeError as e:
            err_str = _(
                "An error occured during the processing of your payment."
                "We will look into the matter and contact you as soon as "
                "possible."
            )
            logger.info(err_str)
            return render_error(
                request,
                err_str
            )
            
        except Exception as e:
            err_str = _(
                "Ann error occurred during the processing of your payment."
                "You will not be charged. Please try again."
            )
            logger.error(err_str)
            return render_error(
                request,
                err_str
            )

        else:
            order = get_object_or_404(ProjectInvestment, uuid=uuid_str)
            project = get_project(request)
            if ((int(float(order.pledged * 100)) == charge["amount"])
                and (str(order.uuid) == charge["metadata"]["uuid"])):
                # mark the order as paid
                order.paid = True
                order.save()
                # count paid ProjectInvestments with date inf or equal this
                # to investment date
                rank = (
                    ProjectInvestment.objects
                    .filter(paid=True)
                    .filter(project=project)
                    .filter(datetime__lte=order.datetime)
                    .count()
                )
                if request.user.is_authenticated:
                    userid = request.user.id

                handle_tweet_investment.apply_async(
                    args=(
                        userid,
                        rank,
                        order.public,
                        project.id
                    )
                )
                return render(
                    request,
                    'crowdfunding/stripe_charge_success.html'
                )
            else:
                return render(
                    request,
                    'crowdfunding/stripe_charge_mismatch.html'
                )
    else:
        return redirect('/financement/')
        
"""
@csrf_exempt
def payment_done(request):
    return render(request, 'crowdfunding/payment_done.html')
""" 

""" 
@csrf_exempt
def payment_canceled(request):
    return render(request, 'crowdfunding/payment_canceled.html')
"""

class ProjectInvestmentView(ListView):

    context_object_name = 'investment_list'
    queryset = ProjectInvestment.objects.all()
    template_name = 'crowdfunding/fund.html'
    
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        project = get_project(self.request)
        if not project:
            return
        tier_lst = []
        if Tier.objects.filter(project=project).count():
            for t in Tier.objects.filter(project=project):
                tier = {}
                tier['title']= t.title
                tier['emoji']= t.emoji
                tier['description']= t.description
                tier['funder_lst'] = list(ProjectInvestment.objects.
                                          filter(paid=True).
                                          filter(public=True).
                                          filter(project=project).
                                          filter(pledged__gte=t.min, pledged__lte=t.max))
                tier_lst.append(tier)
        else:
            context['funder_lst'] = list(ProjectInvestment.objects.
                                          filter(paid=True).
                                          filter(public=True).
                                          filter(project=project).
                                          order_by('name').
                                          distinct('name'))
        context['tier_lst'] = tier_lst
        
        # Replaced by custom templatetag
        #context['investor_count'] = (ProjectInvestment
        #                             .objects
        #                             .filter(paid=True)
        #                             .filter(project=project)
        #                             .distinct('user')
        #                             .count())   
        return context