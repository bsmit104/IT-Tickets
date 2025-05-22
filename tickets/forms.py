from django import forms
from .models import Ticket, User

class TicketForm(forms.ModelForm):
    assignee = forms.ModelChoiceField(queryset=User.objects.filter(is_staff=True), required=False)

    class Meta:
        model = Ticket
        fields = ['title', 'description', 'priority', 'status', 'assignee', 'resolution_notes', 
                 'user_name', 'user_email', 'user_phone', 'user_role', 'user_location']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make user fields optional for staff
        self.fields['user_name'].required = False
        self.fields['user_email'].required = False
        self.fields['user_phone'].required = False
        self.fields['user_role'].required = False
        self.fields['user_location'].required = False