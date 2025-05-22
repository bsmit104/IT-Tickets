from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from tickets.models import Ticket
from faker import Faker
import random
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Generate mock ticket data for campus IT support'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing tickets before creating new ones',
        )

    def handle(self, *args, **kwargs):
        fake = Faker()
        
        # Change distribution to have more OPEN tickets
        statuses = ['OPEN', 'OPEN', 'OPEN', 'IN_PROGRESS', 'RESOLVED', 'CLOSED']
        
        # Create some test users if none exist
        if not User.objects.filter(is_staff=True).exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin')
            User.objects.create_user('helpdesk', 'helpdesk@campus.edu', 'helpdesk', is_staff=True)
            User.objects.create_user('technician', 'tech@campus.edu', 'tech', is_staff=True)
            User.objects.create_user('brayden', 'brayden@campus.edu', 'testpassword', is_staff=True)
        
        users = list(User.objects.filter(is_staff=True))
        
        if kwargs['clear']:
            Ticket.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Cleared existing tickets'))
        
        # Campus-specific data
        campus_buildings = [
            'University Library', 'Student Union', 'Science Building', 'Engineering Hall',
            'Arts Center', 'Business School', 'Residence Hall A', 'Residence Hall B',
            'Sports Complex', 'Administration Building', 'Health Center', 'Campus Cafe'
        ]
        
        user_roles = ['Student', 'Faculty', 'Staff', 'Teaching Assistant', 'Adjunct Faculty', 'Visiting Professor', 'Department Head']
        
        common_issues = [
            {
                'title': 'Cannot connect to campus WiFi',
                'description': 'Having trouble connecting to the campus wireless network. My device shows the network but won\'t connect successfully.'
            },
            {
                'title': 'Password reset needed for student portal',
                'description': 'I forgot my password and need help resetting it. I\'ve tried the reset option but didn\'t receive an email.'
            },
            {
                'title': 'Classroom projector not working',
                'description': 'The projector in room {0} isn\'t displaying from the instructor computer. The screen stays blue when connected.'
            },
            {
                'title': 'Software installation assistance',
                'description': 'Need help installing the required {0} software for my {1} class. Having permission issues on my laptop.'
            },
            {
                'title': 'Printer not working in computer lab',
                'description': 'Unable to print my assignment in the {0} computer lab. The printer shows error code {1}.'
            },
            {
                'title': 'Course management system access issue',
                'description': 'I can\'t access my courses on the learning management system. I\'m enrolled in the class but it doesn\'t appear in my dashboard.'
            },
            {
                'title': 'Email account locked out',
                'description': 'My campus email account is locked. I\'ve tried resetting my password but still can\'t get in.'
            },
            {
                'title': 'Computer lab workstation freezing',
                'description': 'Workstation #{0} in the {1} lab keeps freezing when running {2}. Had to restart multiple times and lost my work.'
            },
            {
                'title': 'Lost data on campus drive',
                'description': 'My files saved to my campus network drive are missing. I saved important documents yesterday but can\'t find them today.'
            },
            {
                'title': 'Smart classroom equipment malfunction',
                'description': 'The smart podium in room {0} isn\'t responding. The touch screen is frozen and none of the controls work.'
            },
            {
                'title': 'VPN connection failing',
                'description': 'Cannot connect to campus VPN from off-campus. The connection initializes but then times out consistently.'
            },
            {
                'title': 'Student ID card not working with printers',
                'description': 'My student ID card won\'t let me release print jobs. The card reader shows error when I scan my card.'
            }
        ]
        
        # Add some critical issue templates
        critical_issues = [
            {
                'title': 'Campus-wide network outage',
                'description': 'The entire campus network is down. Nobody can access the internet or campus resources.'
            },
            {
                'title': 'Final exam software crash',
                'description': 'The testing software for final exams has crashed in the middle of an exam. 30+ students affected.'
            },
            {
                'title': 'Main server room overheating',
                'description': 'Temperature alerts indicate the main server room is reaching critical temperatures. Cooling system may have failed.'
            },
            {
                'title': 'Database security breach detected',
                'description': 'Security monitoring has detected unusual access patterns to the student records database.'
            },
        ]
        
        software_list = ['MATLAB', 'SPSS', 'Adobe Creative Cloud', 'ArcGIS', 'AutoCAD', 'Python', 'R Studio', 'Visual Studio', 'Microsoft Office']
        courses = ['CS101', 'BIO240', 'ENG220', 'PSYCH330', 'BUSN400', 'MATH250', 'PHYS180', 'CHEM210']
        error_codes = ['E-225', 'P-403', 'ERR_CONN_LOST', '0x8007007B', 'SPOOLSV_ERR']
        
        # Create CRITICAL tickets first (mostly OPEN)
        self.stdout.write(self.style.SUCCESS('Creating CRITICAL priority tickets...'))
        for _ in range(5):
            issue = random.choice(critical_issues)
            # 80% chance of being OPEN
            status = 'OPEN' if random.random() < 0.8 else random.choice(['IN_PROGRESS', 'RESOLVED'])
            
            days_ago = random.randint(0, 7)  # More recent
            created_at = timezone.now() - timedelta(days=days_ago)
            updated_at = created_at + timedelta(hours=random.randint(1, 12))
            
            resolution_notes = ""
            if status in ['RESOLVED', 'CLOSED']:
                resolution_notes = "Emergency issue resolved by IT team."

            user_name = fake.name()
            user_email = f"{fake.user_name()}@campus.edu"
            user_phone = f"({random.randint(200, 999)}) {random.randint(200, 999)}-{random.randint(1000, 9999)}"
            user_role = random.choice(user_roles)
            user_location = random.choice(campus_buildings)
            
            Ticket.objects.create(
                title=issue['title'],
                description=issue['description'],
                status=status,
                priority='CRITICAL',
                assignee=random.choice(users) if random.random() > 0.3 else None,
                created_by=random.choice(users),
                created_at=created_at,
                updated_at=updated_at,
                resolution_notes=resolution_notes,
                user_name=user_name,
                user_email=user_email,
                user_phone=user_phone,
                user_role=user_role,
                user_location=user_location
            )
        
        # Create rest of tickets with weighted priorities
        self.stdout.write(self.style.SUCCESS('Creating other tickets...'))
        tickets_created = 5  # Already created 5 CRITICAL tickets
        
        for _ in range(45):  # Create 45 more tickets (total 50)
            # Pick a random issue template
            issue = random.choice(common_issues)
            title = issue['title']
            description = issue['description']
            
            # Format description with random campus-specific details
            if '{' in description:
                if 'room' in description:
                    description = description.format(f"{random.choice(['A', 'B', 'C', 'D'])}-{random.randint(100, 399)}")
                elif 'software' in description:
                    description = description.format(random.choice(software_list), random.choice(courses))
                elif 'lab' in description and 'Workstation' not in description:
                    description = description.format(random.choice(campus_buildings), random.choice(error_codes))
                elif 'Workstation' in description:
                    description = description.format(random.randint(1, 30), random.choice(campus_buildings), random.choice(software_list))
                elif 'error code' in description:
                    description = description.format(random.choice(campus_buildings), random.choice(error_codes))
            
            status = random.choice(statuses)
            
            # Weighted priority selection
            priority_weight = random.random()
            if priority_weight < 0.15:  # 15% chance of CRITICAL
                priority = 'CRITICAL'
            elif priority_weight < 0.40:  # 25% chance of HIGH
                priority = 'HIGH'
            elif priority_weight < 0.75:  # 35% chance of MEDIUM
                priority = 'MEDIUM'
            else:  # 25% chance of LOW
                priority = 'LOW'
            
            # Generate random dates within the last 30 days
            days_ago = random.randint(0, 30)
            created_at = timezone.now() - timedelta(days=days_ago)
            updated_at = created_at + timedelta(days=random.randint(0, days_ago))
            
            resolution_notes = ""
            if status in ['RESOLVED', 'CLOSED']:
                resolution_templates = [
                    "Issue resolved by resetting user account credentials. User now has access.",
                    "Reinstalled printer drivers and confirmed printing now works properly.",
                    "Replaced faulty hardware component and tested functionality.",
                    "Provided user with instructions to clear browser cache and cookies which resolved the issue.",
                    "Updated software to latest version which fixed the reported bug.",
                    "Reconfigured network settings and confirmed connectivity is restored."
                ]
                resolution_notes = random.choice(resolution_templates)

            # Generate campus user information
            user_name = fake.name()
            user_email = f"{fake.user_name()}@campus.edu"
            user_phone = f"({random.randint(200, 999)}) {random.randint(200, 999)}-{random.randint(1000, 9999)}"
            user_role = random.choice(user_roles)
            user_location = random.choice(campus_buildings)
            
            try:
                Ticket.objects.create(
                    title=title,
                    description=description,
                    status=status,
                    priority=priority,
                    assignee=random.choice(users) if random.random() > 0.3 else None,
                    created_by=random.choice(users),
                    created_at=created_at,
                    updated_at=updated_at,
                    resolution_notes=resolution_notes,
                    user_name=user_name,
                    user_email=user_email,
                    user_phone=user_phone,
                    user_role=user_role,
                    user_location=user_location
                )
                tickets_created += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating ticket: {str(e)}'))
                
        self.stdout.write(self.style.SUCCESS(f'Successfully generated {tickets_created} campus IT support tickets'))