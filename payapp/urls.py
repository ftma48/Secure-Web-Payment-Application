from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('send/', views.send_payment, name='send_payment'),
    path('request/', views.request_payment, name='request_payment'),
    path('notifications/', views.notifications, name='notifications'),
    path('handle_request/<int:request_id>/', views.handle_request, name='handle_request'),
]