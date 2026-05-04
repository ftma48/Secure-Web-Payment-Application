from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('send/', views.send_payment, name='send_payment'),
    path('request/', views.request_payment, name='request_payment'),
    path('notifications/', views.notifications, name='notifications'),
    path('handle_request/<int:request_id>/', views.handle_request, name='handle_request'),
    path('admin/users/', views.admin_users, name='admin_users'),
    path('admin/transactions/', views.admin_transactions, name='admin_transactions'),
    path('admin/register/', views.admin_register, name='admin_register'),
]