from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.db.models import Q, Count, Avg, F, ExpressionWrapper, fields, Case, When
from .models import Ticket, ActionLog, TicketHistory
from .forms import TicketForm
from datetime import datetime, timedelta
from collections import Counter
import csv
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.models import User

@login_required
def ticket_list(request):
    query = request.GET.get('q', '')
    
    # Define priority order for sorting
    priority_order = Case(
        When(priority='CRITICAL', then=0),
        When(priority='HIGH', then=1),
        When(priority='MEDIUM', then=2),
        When(priority='LOW', then=3),
    )
    
    # Always filter to only open tickets
    tickets = Ticket.objects.filter(status='OPEN')
    
    if query:
        # Apply search filters while maintaining open status
        tickets = tickets.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(status__icontains=query) |
            Q(priority__icontains=query) |
            Q(assignee__username__icontains=query) |
            Q(created_by__username__icontains=query) |
            Q(user_name__icontains=query) |
            Q(user_email__icontains=query) |
            Q(user_phone__icontains=query) |
            Q(user_role__icontains=query) |
            Q(user_location__icontains=query) |
            Q(resolution_notes__icontains=query)
        )
    
    # Always order by priority (highest first) and then by creation date (oldest first)
    tickets = tickets.order_by(priority_order, 'created_at')
    
    # Limit to 10 tickets only after ordering
    tickets = tickets[:10]
    
    recently_viewed_ids = request.session.get('recently_viewed', [])
    recently_viewed = Ticket.objects.filter(id__in=recently_viewed_ids)[:5]
    recent_actions = ActionLog.objects.order_by('-timestamp')[:7]
    
    # Count open tickets instead of all tickets
    total_open_tickets = Ticket.objects.filter(status='OPEN').count()
    
    # Calculate average resolution time more accurately:
    # 1. Include both RESOLVED and CLOSED tickets
    # 2. Only consider tickets resolved in the last 30 days for a more realistic metric
    # 3. Limit the maximum resolution time to avoid outliers skewing the average
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    resolved_tickets = Ticket.objects.filter(
        status__in=['RESOLVED', 'CLOSED'],
        updated_at__gte=thirty_days_ago
    )
    
    if resolved_tickets.exists():
        total_resolution_hours = 0
        ticket_count = 0
        
        for ticket in resolved_tickets:
            # Calculate hours between creation and resolution
            delta = ticket.updated_at - ticket.created_at
            hours = delta.total_seconds() / 3600
            
            # Cap resolution time at 336 hours (2 weeks) to prevent outliers
            capped_hours = min(hours, 336)
            total_resolution_hours += capped_hours
            ticket_count += 1
        
        avg_resolution_hours = round(total_resolution_hours / ticket_count, 1) if ticket_count > 0 else 0
    else:
        avg_resolution_hours = 0
    
    # Define priority order (highest to lowest)
    priority_order = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
    
    # Find the highest priority among open tickets
    open_tickets = Ticket.objects.filter(status='OPEN')
    highest_priority = 'LOW'  # Default if no open tickets
    
    if open_tickets.exists():
        # Get all priorities of open tickets
        ticket_priorities = open_tickets.values_list('priority', flat=True)
        
        # Find the highest priority based on the defined order
        for priority in priority_order:
            if priority in ticket_priorities:
                highest_priority = priority
                break
    
    return render(request, 'tickets/ticket_list.html', {
        'tickets': tickets,
        'query': query,
        'recently_viewed': recently_viewed,
        'recent_actions': recent_actions,
        'total_open_tickets': total_open_tickets,
        'avg_resolution_time': avg_resolution_hours,
        'top_priority': highest_priority
    })

@login_required
def all_tickets(request):
    query = request.GET.get('q', '')
    if query:
        # Search across all tickets regardless of status
        tickets = Ticket.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(status__icontains=query) |
            Q(priority__icontains=query) |
            Q(assignee__username__icontains=query) |
            Q(created_by__username__icontains=query) |
            Q(user_name__icontains=query) |
            Q(user_email__icontains=query) |
            Q(user_phone__icontains=query) |
            Q(user_role__icontains=query) |
            Q(user_location__icontains=query) |
            Q(resolution_notes__icontains=query)
        )
    else:
        # Get all tickets
        tickets = Ticket.objects.all()
        
        # Define priority order for sorting
        priority_order = Case(
            When(priority='CRITICAL', then=0),
            When(priority='HIGH', then=1),
            When(priority='MEDIUM', then=2),
            When(priority='LOW', then=3),
        )
        
        # Order by priority (highest first) and then by creation date (oldest first)
        tickets = tickets.order_by(priority_order, 'created_at')
    
    return render(request, 'tickets/all_tickets.html', {
        'tickets': tickets,
        'query': query,
    })

@login_required
def completed_tickets(request):
    query = request.GET.get('q', '')
    if query:
        tickets = Ticket.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(status__icontains=query) |
            Q(priority__icontains=query) |
            Q(assignee__username__icontains=query) |
            Q(created_by__username__icontains=query) |
            Q(user_name__icontains=query) |
            Q(user_email__icontains=query) |
            Q(user_phone__icontains=query) |
            Q(user_role__icontains=query) |
            Q(user_location__icontains=query) |
            Q(resolution_notes__icontains=query)
        ).filter(status__in=['RESOLVED', 'CLOSED'])
    else:
        # Get only completed tickets (resolved and closed)
        tickets = Ticket.objects.filter(status__in=['RESOLVED', 'CLOSED'])
        
        # Order by updated_at date (newest completed first)
        tickets = tickets.order_by('-updated_at')
    
    return render(request, 'tickets/completed_tickets.html', {
        'tickets': tickets,
        'query': query,
    })

@login_required
def ticket_detail(request, pk):
    ticket = Ticket.objects.get(pk=pk)
    recently_viewed = request.session.get('recently_viewed', [])
    if pk not in recently_viewed:
        recently_viewed.insert(0, pk)
        request.session['recently_viewed'] = recently_viewed[:5]
    ActionLog.objects.create(user=request.user, action='viewed', ticket_title=ticket.title)
    ticket_history = ticket.ticket_history.all().order_by('-timestamp')[:5]
    return render(request, 'tickets/ticket_detail.html', {
        'ticket': ticket,
        'ticket_history': ticket_history
    })

@login_required
def add_ticket(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.created_by = request.user
            ticket.save()
            ActionLog.objects.create(user=request.user, action='created', ticket_title=ticket.title)
            return redirect('ticket_list')
    else:
        form = TicketForm()
    return render(request, 'tickets/add_ticket.html', {'form': form})

@login_required
def edit_ticket(request, pk):
    ticket = Ticket.objects.get(pk=pk)
    if request.method == 'POST':
        form = TicketForm(request.POST, instance=ticket)
        if form.is_valid():
            old_data = Ticket.objects.get(pk=pk).__dict__
            form.save()
            new_data = Ticket.objects.get(pk=pk).__dict__
            for field in form.changed_data:
                ActionLog.objects.create(user=request.user, action='edited', ticket_title=ticket.title)
                TicketHistory.objects.create(
                    ticket=ticket,
                    user=request.user,
                    field_changed=field,
                    old_value=str(old_data.get(field, '')),
                    new_value=str(new_data.get(field, ''))
                )
            return redirect('ticket_list')
    else:
        form = TicketForm(instance=ticket)
    return render(request, 'tickets/edit_ticket.html', {'form': form, 'ticket': ticket})

@login_required
def delete_ticket(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    if request.method == 'POST':
        ticket_title = ticket.title
        ticket.delete()
        ActionLog.objects.create(user=request.user, action='deleted', ticket_title=ticket_title)
        return redirect('ticket_list')
    return render(request, 'tickets/delete_ticket.html', {'ticket': ticket})

@login_required
def export_tickets(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="tickets_export.csv"'
    writer = csv.writer(response)
    writer.writerow(['Title', 'Description', 'Status', 'Priority', 'Assignee', 'Created By', 'Created At', 'Updated At', 'Resolution Notes'])
    for ticket in Ticket.objects.all():
        writer.writerow([
            ticket.title,
            ticket.description,
            ticket.status,
            ticket.priority,
            ticket.assignee.username if ticket.assignee else '',
            ticket.created_by.username,
            ticket.created_at,
            ticket.updated_at,
            ticket.resolution_notes
        ])
    ActionLog.objects.create(user=request.user, action='exported', ticket_title='All Tickets')
    return response

@login_required
def ticket_chart(request):
    tickets = Ticket.objects.all()

    # Bar Chart: Tickets by Status
    status_counts = {'OPEN': 0, 'IN_PROGRESS': 0, 'RESOLVED': 0, 'CLOSED': 0}
    for t in tickets:
        status_counts[t.status] += 1
    bar_data = {
        'labels': list(status_counts.keys()),
        'counts': list(status_counts.values())
    }

    # Pie Chart: Tickets by Priority
    priorities = [t.priority for t in tickets]
    priority_counts = Counter(priorities).most_common(4)
    other_count = len(priorities) - sum(count for _, count in priority_counts)
    pie_labels = [p for p, _ in priority_counts] + (['Other'] if other_count > 0 else [])
    pie_values = [count for _, count in priority_counts] + ([other_count] if other_count > 0 else [])
    pie_data = {
        'labels': pie_labels,
        'counts': pie_values
    }

    # Line Chart: Tickets Created Over Time
    today = datetime.now().date()
    last_year = today - timedelta(days=365)
    monthly_counts = []
    labels = []
    current_date = last_year
    while current_date <= today:
        next_month = (current_date.replace(day=1) + timedelta(days=32)).replace(day=1)
        count = Ticket.objects.filter(created_at__date__gte=current_date, created_at__date__lt=next_month).count()
        monthly_counts.append(count)
        labels.append(current_date.strftime('%b %Y'))
        current_date = next_month
    line_data = {
        'labels': labels,
        'counts': monthly_counts
    }

    # Heatmap: Priority by Status
    heatmap_data = []
    priority_list = list(set(priorities))
    for priority in priority_list[:4]:
        row = {'priority': priority}
        for status in status_counts.keys():
            count = Ticket.objects.filter(priority=priority, status=status).count()
            row[status] = count
        heatmap_data.append(row)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        chart_type = request.GET.get('type', 'bar')
        if chart_type == 'bar':
            return JsonResponse(bar_data)
        elif chart_type == 'pie':
            return JsonResponse(pie_data)
        elif chart_type == 'line':
            return JsonResponse(line_data)
        elif chart_type == 'heatmap':
            return JsonResponse({'data': heatmap_data})
    return render(request, 'tickets/ticket_chart.html')

def public_ticket_form(request):
    """View for public users to submit tickets without needing an account"""
    if request.method == 'POST':
        # Get form data
        title = request.POST.get('title', '')
        description = request.POST.get('description', '')
        priority = request.POST.get('priority', 'MEDIUM')
        
        # Get user information fields
        user_name = request.POST.get('name', '')
        user_email = request.POST.get('email', '')
        user_phone = request.POST.get('phone', '')
        user_role = request.POST.get('role', '')
        user_location = request.POST.get('location', '')
        
        # Find or create a default staff user to assign as the creator
        staff_user = User.objects.filter(is_staff=True).first()
        if not staff_user:
            # If no staff users exist, create a system user
            staff_user = User.objects.create_user(
                username='system',
                email='system@example.com',
                password=User.objects.make_random_password(),
                is_staff=True
            )
        
        # Create the ticket with proper user information fields
        ticket = Ticket.objects.create(
            title=title,
            description=description,
            status='OPEN',
            priority=priority,
            created_by=staff_user,
            created_at=timezone.now(),
            user_name=user_name,
            user_email=user_email,
            user_phone=user_phone,
            user_role=user_role,
            user_location=user_location
        )
        
        # Log the action
        ActionLog.objects.create(
            user=staff_user,
            action='created via public form',
            ticket_title=ticket.title
        )
        
        # Return success response
        return render(request, 'tickets/public_ticket_form.html', {
            'form_submitted': True,
            'ticket_id': ticket.id
        })
    
    # For GET requests, just show the form
    return render(request, 'tickets/public_ticket_form.html')

# For debugging only
def debug_ticket_order(request):
    """Temporary view to debug ticket ordering"""
    # Define priority order for sorting
    priority_order = Case(
        When(priority='CRITICAL', then=0),
        When(priority='HIGH', then=1),
        When(priority='MEDIUM', then=2),
        When(priority='LOW', then=3),
    )
    
    # Get all open tickets sorted by priority and creation date
    open_tickets = Ticket.objects.filter(status='OPEN').order_by(priority_order, 'created_at')
    
    # Debug info
    results = {
        'total_open_tickets': open_tickets.count(),
        'tickets': []
    }
    
    # Add ticket details
    for ticket in open_tickets[:20]:  # Show more than 10 for debugging
        results['tickets'].append({
            'id': ticket.id,
            'title': ticket.title,
            'priority': ticket.priority,
            'created_at': str(ticket.created_at),
            'user_name': ticket.user_name,
            'assignee': ticket.assignee.username if ticket.assignee else 'Unassigned'
        })
    
    # Group by priority for easier analysis
    priority_counts = {
        'CRITICAL': Ticket.objects.filter(status='OPEN', priority='CRITICAL').count(),
        'HIGH': Ticket.objects.filter(status='OPEN', priority='HIGH').count(),
        'MEDIUM': Ticket.objects.filter(status='OPEN', priority='MEDIUM').count(),
        'LOW': Ticket.objects.filter(status='OPEN', priority='LOW').count(),
    }
    results['priority_counts'] = priority_counts
    
    return JsonResponse(results)