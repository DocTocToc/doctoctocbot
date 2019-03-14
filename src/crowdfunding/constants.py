import braintree

TRANSACTION_SUCCESS_STATUSES = [
    braintree.Transaction.Status.Authorized,
    braintree.Transaction.Status.Authorizing,
    braintree.Transaction.Status.Settled,
    braintree.Transaction.Status.SettlementConfirmed,
    braintree.Transaction.Status.SettlementPending,
    braintree.Transaction.Status.Settling,
    braintree.Transaction.Status.SubmittedForSettlement
]


ITEM_NAME = "Développement d'1 nouvelle fonctionnalité pour la suite de logiciels pour professionnels de santé doctoctoc.net"
HOURLY_RATE_EUR = 60