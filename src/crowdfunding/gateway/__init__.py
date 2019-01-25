import os
from django.conf import settings
import braintree

if settings.BRAINTREE_PRODUCTION:
    braintree_env = braintree.Environment.Production
else:
    braintree_env = braintree.Environment.Sandbox

gateway = braintree.BraintreeGateway(
    braintree.Configuration(
        environment=braintree_env,
        merchant_id=settings.BRAINTREE_MERCHANT_ID,
        public_key=settings.BRAINTREE_PUBLIC_KEY,
        private_key=settings.BRAINTREE_PRIVATE_KEY
    )
)

def generate_client_token():
    return gateway.client_token.generate()

def transact(options):
    return gateway.transaction.sale(options)

def find_transaction(id):
    return gateway.transaction.find(id)
