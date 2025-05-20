from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.db.models import Q, Count, Avg, F, ExpressionWrapper, fields
from .models import Ticket, ActionLog, TicketHistory
from .forms import TicketForm
from datetime import datetime, timedelta
from collections import Counter
import csv

@login_required
def ticket_list(request):
    query = request.GET.get('q', '')
    if query:
        tickets = Ticket.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(status__icontains=query) |
            Q(priority__icontains=query)
        )
    else:
        tickets = Ticket.objects.all()
    recently_viewed_ids = request.session.get('recently_viewed', [])
    recently_viewed = Ticket.objects.filter(id__in=recently_viewed_ids)[:5]
    recent_actions = ActionLog.objects.order_by('-timestamp')[:7]
    total_tickets = Ticket.objects.count()
    avg_resolution_time = Ticket.objects.filter(status='RESOLVED').aggregate(
        avg_time=Avg(ExpressionWrapper(F('updated_at') - F('created_at'), output_field=fields.DurationField()))
    )['avg_time'] or 0
    top_priority = Ticket.objects.values('priority').annotate(count=Count('id')).order_by('-count').first()
    return render(request, 'tickets/ticket_list.html', {
        'tickets': tickets,
        'query': query,
        'recently_viewed': recently_viewed,
        'recent_actions': recent_actions,
        'total_tickets': total_tickets,
        'avg_resolution_time': round(avg_resolution_time.total_seconds() / 3600, 1) if avg_resolution_time else 0,
        'top_priority': top_priority['priority'] if top_priority else 'N/A'
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