from django.core.management.base import BaseCommand
from tickets.models import Ticket

class Command(BaseCommand):
    help = 'Check a ticket description'

    def handle(self, *args, **kwargs):
        ticket = Ticket.objects.first()
        if ticket:
            self.stdout.write(self.style.SUCCESS(f'Ticket Title: {ticket.title}'))
            self.stdout.write(self.style.SUCCESS('Ticket Description:'))
            self.stdout.write(ticket.description)
        else:
            self.stdout.write(self.style.ERROR('No tickets found')) 