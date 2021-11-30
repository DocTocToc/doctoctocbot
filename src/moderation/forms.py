import logging
from django import forms
from django.utils.translation import ugettext_lazy as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from discourse.models import AccessControl

logger = logging.getLogger(__name__)

class SelfModerationForm(forms.Form):
    
    def __init__(self, *args, **kwargs):
        super(SelfModerationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'self-moderation-form'
        self.helper.form_class = 'blueForms'
        self.helper.form_action = 'moderation:self'
        self.helper.add_input(Submit('submit', _('Submit')))
        self.helper.form_method = 'post'

    try:
        CATEGORY_CHOICES = list(
            AccessControl.objects.filter(authorize=True).values_list(
                'category__name',
                'category__label'
            )
        )
    except (TypeError, AccessControl.DoesNotExist) as e:
        logger.error(e)
        CATEGORY_CHOICES = []
    CATEGORY_CHOICES.insert(0, ('', _('None of those categories')))
    category = forms.ChoiceField(
        label=_('Please choose a category'),
        choices=CATEGORY_CHOICES,
        required=False,
    )
    certify = forms.BooleanField(
        label=_("I hereby certify that I do belong to this category.")    
    )
    message = forms.CharField(
        widget=forms.Textarea,
        label=_(
            "This community is mostly comprised of people belonging to the "
            "listed categories. If you don't belong to any of them but you "
            "still want to join, please tell us why "
            "and we will review your application."
        ),
        required=False,
    )