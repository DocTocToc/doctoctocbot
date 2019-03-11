"""
A base contact form for allowing users to send email messages through
a web interface.

"""

import gnupg
import logging

from django import forms
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template import loader
from django.utils.translation import ugettext_lazy as _

logger = logging.getLogger(__name__)


class ContactForm(forms.Form):
    """
    The base contact form class from which all contact form classes
    should inherit.

    """
    ciphertext = forms.CharField()
    
    from_email = settings.DEFAULT_FROM_EMAIL

    recipient_list = [mail_tuple[1] for mail_tuple in settings.MANAGERS]

    subject_template_name = "gpg_contact_form/contact_form_subject.txt"

    template_name = 'gpg_contact_form/contact_form.txt'

    def __init__(self, data=None, files=None, request=None,
                 recipient_list=None, *args, **kwargs):
        if request is None:
            raise TypeError("Keyword argument 'request' must be supplied")
        self.request = request
        if recipient_list is not None:
            self.recipient_list = recipient_list
        super(ContactForm, self).__init__(data=data, files=files,
                                          *args, **kwargs)
        self.fields['ciphertext'].strip = False

    def clean_ciphertext(self):
        data = self.data['ciphertext']
        gpg = gnupg.GPG(gnupghome=settings.GNUPGHOME)
        logger.debug(gpg)
        logger.debug("data: %s" % data)
        logger.debug("type of data: %s" % type(data))
        verified = gpg.verify(data)
        if not (verified and verified.fingerprint in settings.GNUPG_PUBLIC_KEYS):
            raise forms.ValidationError(_("NO SPAM ALLOWED ON THIS SERVER SORRY!"), code='invalid')
        
        begin = '-----BEGIN PGP MESSAGE-----'
        end = '-----END PGP MESSAGE-----'
        dash_space = "- "
        
        try:
            begin_idx = data.index(begin)
        except ValueError as e:
            logger.debug(e.args)
            raise forms.ValidationError(
                _("The message must be encrypted Header %(begin)s is missing"),
                params={'begin': begin},
            )
            return data
        
        try:
            end_idx = data.index("".join([dash_space, end]))
        except ValueError as e:
            logger.debug(e.args)
            raise forms.ValidationError(
                _("The message must be encrypted Header %(begin)s is missing"),
                params={'begin': end},
            )
            return data
        s = slice(begin_idx, end_idx)
        return "".join([data[s], end])

    def message(self):
        """
        Return the ciphertext.

        """
        template_name = self.template_name() if \
            callable(self.template_name) \
            else self.template_name
        return loader.render_to_string(
            template_name, self.get_context(), request=self.request)
        #return self.get_context()["ciphertext"]

    def subject(self):
        """
        Render the subject of the message to a string.

        """
        template_name = self.subject_template_name() if \
            callable(self.subject_template_name) \
            else self.subject_template_name
        subject = loader.render_to_string(
            template_name, self.get_site(), request=self.request
        )
        return ''.join(subject.splitlines())

    def get_context(self):
        """
        Return the context used to render the templates for the email
        subject and body.

        By default, this context includes:

        * All of the validated values in the form, as variables of the
          same names as their fields.

        * The current ``Site`` object, as the variable ``site``.

        * Any additional variables added by context processors (this
          will be a ``RequestContext``).

        """
        if not self.is_valid():
            raise ValueError(
                "Cannot generate Context from invalid contact form"
            )
        return dict(self.cleaned_data, site=get_current_site(self.request))
    
    def get_site(self):
        """
        Return a dict containing the  current ``Site`` object, as the variable ``site``.
        """
        return dict(site=get_current_site(self.request))

    def get_message_dict(self):
        """
        Generate the various parts of the message and return them in a
        dictionary, suitable for passing directly as keyword arguments
        to ``django.core.mail.send_mail()``.

        By default, the following values are returned:

        * ``from_email``

        * ``message``

        * ``recipient_list``

        * ``subject``

        """
        if not self.is_valid():
            raise ValueError(
                "Message cannot be sent from invalid contact form"
            )
        message_dict = {}
        for message_part in ('from_email', 'message',
                             'recipient_list', 'subject'):
            attr = getattr(self, message_part)
            message_dict[message_part] = attr() if callable(attr) else attr
        return message_dict

    def save(self, fail_silently=False):
        """
        Build and send the email message.

        """
        send_mail(fail_silently=fail_silently, **self.get_message_dict())