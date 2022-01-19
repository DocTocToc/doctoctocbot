from django.contrib import admin
from django.db import models
from textareacounter.widget import TextareaWithCounter

class TextAreaCounterAdminMixin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': TextareaWithCounter},
    }
    class Media:
        css = {
            "all": ("textareacounter/textareacounter.css", )
        }
        js = (
            "https://code.jquery.com/jquery-3.6.0.slim.min.js",
            "textareacounter/textareacounter.js",
        )