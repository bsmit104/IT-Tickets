from django.contrib import admin
from .models import Ticket, TicketHistory, ActionLog

admin.site.register(Ticket)
admin.site.register(TicketHistory)
admin.site.register(ActionLog)