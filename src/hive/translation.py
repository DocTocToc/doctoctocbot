from modeltranslation.translator import register, TranslationOptions

from hive.models import NotificationService

@register(NotificationService)
class NotificationServiceTranslationOptions(TranslationOptions):
    fields = ('label', 'description',)