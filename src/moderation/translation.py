from modeltranslation.translator import translator, TranslationOptions

from .models import Category

class CategoryTranslationOptions(TranslationOptions):
    fields = ('label', 'description')
    
    
translator.register(Category, CategoryTranslationOptions)