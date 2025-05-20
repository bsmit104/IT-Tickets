import os
import re
import django
from django.template.loader import render_to_string
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'IT_Tickets.settings')
django.setup()

# Render the base template
html = render_to_string('tickets/base.html', {})

# Find all CSS files being loaded
css_links = re.findall(r'<link[^>]*?rel=["\']\s*stylesheet\s*["\'][^>]*?href=["\'](.*?)["\']', html)

print("CSS FILES LOADED:")
for link in css_links:
    print(f"- {link}")

# Check for inline styles
inline_styles = re.findall(r'<style[^>]*?>(.*?)</style>', html, re.DOTALL)

if inline_styles:
    print("\nINLINE STYLES:")
    for style in inline_styles:
        print(style)
else:
    print("\nNo inline styles found.") 