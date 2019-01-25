from django.contrib import messages
from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect

from .gateway import generate_client_token, transact, find_transaction

from .constants import TRANSACTION_SUCCESS_STATUSES

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