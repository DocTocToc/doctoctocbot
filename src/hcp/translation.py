from modeltranslation.translator import translator, TranslationOptions

from hcp.models import Taxonomy

class TaxonomyTranslationOptions(TranslationOptions):
    fields = (
        'grouping',
        'classification',
        'specialization',
        'definition',
    )
    
translator.register(Taxonomy, TaxonomyTranslationOptions)
