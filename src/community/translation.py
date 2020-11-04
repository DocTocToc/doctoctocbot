from modeltranslation.translator import translator, TranslationOptions

from .models import TextDescription, AccessLevel


class TextDescriptionTranslationOptions(TranslationOptions):
    fields = ('label', 'description')


class AccessLevelTranslationOptions(TranslationOptions):
    fields = ('label', 'description')

   
translator.register(TextDescription, TextDescriptionTranslationOptions)
translator.register(AccessLevel, AccessLevelTranslationOptions)