from django.contrib import admin
from request.models import Queue, Process

admin.site.register(Queue)
admin.site.register(Process)
#admin.site.register(Queue, QueueAdmin)
#admin.site.register(Process, ProcessAdmin)