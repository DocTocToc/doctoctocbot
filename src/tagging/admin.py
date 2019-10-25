from django.contrib import admin

from tagging.models import Queue, Process, Category

admin.site.register(Queue)
admin.site.register(Process)
admin.site.register(Category)