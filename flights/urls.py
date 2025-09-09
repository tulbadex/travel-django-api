from django.urls import path
from . import views

app_name = 'flights'

urlpatterns = [
    path('airports/', views.AirportListView.as_view(), name='airport_list'),
    path('airlines/', views.AirlineListView.as_view(), name='airline_list'),
    path('search/', views.search_flights, name='search_flights'),
    path('bookings/', views.FlightBookingListCreateView.as_view(), name='booking_list_create'),
    path('bookings/<int:pk>/', views.FlightBookingDetailView.as_view(), name='booking_detail'),
]