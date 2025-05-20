from django import forms
from .models import Ticket, User

class TicketForm(forms.ModelForm):
    assignee = forms.ModelChoiceField(queryset=User.objects.filter(is_staff=True), required=False)

    class Meta:
        model = Ticket
        fields = ['title', 'description', 'priority', 'status', 'assignee', 'resolution_notes']