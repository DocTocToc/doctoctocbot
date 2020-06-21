from modeltranslation.translator import translator, TranslationOptions

from .models import TextDescription


class TextDescriptionTranslationOptions(TranslationOptions):
    fields = ('label', 'description')

   
translator.register(TextDescription, TextDescriptionTranslationOptions)