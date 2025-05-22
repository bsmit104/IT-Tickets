from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Ticket(models.Model):
    STATUS_CHOICES = (
        ('OPEN', 'Open'),
        ('IN_PROGRESS', 'In Progress'),
        ('RESOLVED', 'Resolved'),
        ('CLOSED', 'Closed'),
    )
    PRIORITY_CHOICES = (
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='LOW')
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tickets')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    resolution_notes = models.TextField(blank=True)

    # User information fields
    user_name = models.CharField(max_length=100, blank=True)
    user_email = models.EmailField(max_length=100, blank=True)
    user_phone = models.CharField(max_length=50, blank=True)
    user_role = models.CharField(max_length=50, blank=True)
    user_location = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.title

class TicketHistory(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='ticket_history')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    field_changed = models.CharField(max_length=50)
    old_value = models.TextField(blank=True)
    new_value = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} changed {self.field_changed} for {self.ticket.title}"

class ActionLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=50)
    ticket_title = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} {self.action} {self.ticket_title}"