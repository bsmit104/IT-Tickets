from django.urls import path
from . import views

urlpatterns = [
    path('', views.ticket_list, name='ticket_list'),
    path('ticket/<int:pk>/', views.ticket_detail, name='ticket_detail'),
    path('add/', views.add_ticket, name='add_ticket'),
    path('edit/<int:pk>/', views.edit_ticket, name='edit_ticket'),
    path('delete/<int:pk>/', views.delete_ticket, name='delete_ticket'),
    path('export/', views.export_tickets, name='export_tickets'),
    path('chart/', views.ticket_chart, name='ticket_chart'),
]