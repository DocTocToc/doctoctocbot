from django.contrib import admin

from invitations.models import Invitation
from invite.models import CategoryInvitation

admin.site.register(Invitation)