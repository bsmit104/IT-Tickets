from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from tickets.models import Ticket
from faker import Faker
import random
from django.utils import timezone

class Command(BaseCommand):
    help = 'Generate mock ticket data'

    def handle(self, *args, **kwargs):
        fake = Faker()
        statuses = ['OPEN', 'IN_PROGRESS', 'RESOLVED', 'CLOSED']
        priorities = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
        issue_types = [
            "Network outage",
            "Software crash",
            "Password reset",
            "Hardware failure",
            "Access issue",
            "Server maintenance",
            "Email not working"
        ]

        # Ensure at least one staff user exists
        users = User.objects.filter(is_staff=True)
        if not users.exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'Yatzsql1', is_staff=True)
            users = User.objects.filter(is_staff=True)

        for _ in range(60):
            created_at = fake.date_time_between(start_date="-1y", end_date="now")
            updated_at = created_at if random.random() < 0.3 else fake.date_time_between(start_date=created_at, end_date="now")
            Ticket.objects.create(
                title=f"{random.choice(issue_types)}: {fake.sentence(nb_words=3)}",
                description=fake.paragraph(nb_sentences=3),
                status=random.choice(statuses),
                priority=random.choice(priorities),
                assignee=random.choice(users) if random.random() > 0.3 else None,
                created_by=random.choice(users),
                created_at=created_at,
                updated_at=updated_at,
                resolution_notes=fake.paragraph(nb_sentences=2) if random.random() > 0.5 and random.choice(statuses) in ['RESOLVED', 'CLOSED'] else ""
            )
        self.stdout.write(self.style.SUCCESS('Generated 60 mock tickets'))