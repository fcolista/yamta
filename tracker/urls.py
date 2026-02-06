from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('add/', views.add_journey, name='add_journey'),
    path('edit-journey/<int:journey_id>/', views.edit_journey, name='edit_journey'),
    path('delete-journey/<int:journey_id>/', views.delete_journey, name='delete_journey'),
    path('history/', views.history_view, name='history'),
    path('reports/', views.reports_view, name='reports'),
    path('settings/', views.settings_view, name='settings'),
    path('edit-fuel/<int:fuel_id>/', views.edit_fuel, name='edit_fuel'),
    path('delete-fuel/<int:fuel_id>/', views.delete_fuel, name='delete_fuel'),
]
