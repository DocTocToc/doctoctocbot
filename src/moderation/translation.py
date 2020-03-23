from modeltranslation.translator import translator, TranslationOptions

from .models import Category, CategoryMetadata

class CategoryTranslationOptions(TranslationOptions):
    fields = ('label', 'description')

class CategoryMetadataTranslationOptions(TranslationOptions):
    fields = ('label', 'description') 
    
translator.register(Category, CategoryTranslationOptions)
translator.register(CategoryMetadata, CategoryMetadataTranslationOptions)