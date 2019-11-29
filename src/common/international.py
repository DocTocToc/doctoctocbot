from __future__ import absolute_import

import pycountry


countries = sorted([(country.alpha_2, country.name) for country in
                    pycountry.countries])
currencies = sorted([(currency.alpha_3,
                      u'{} ({})'.format(currency.alpha_3, currency.name))
                     for currency in pycountry.currencies])