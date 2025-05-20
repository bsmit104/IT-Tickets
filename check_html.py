import os
import django
from django.template.loader import render_to_string
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'IT_Tickets.settings')
django.setup()

# Render a simple HTML template
html = render_to_string('tickets/base.html', {})

# Print the HTML to see what's being loaded
print(html) 