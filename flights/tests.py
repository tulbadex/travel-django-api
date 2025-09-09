from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from datetime import datetime, timedelta
from django.utils import timezone
from .models import Airport, Airline, Flight, FlightBooking

User = get_user_model()

class AirportModelTest(TestCase):
    def test_create_airport(self):
        airport = Airport.objects.create(
            code='LAX',
            name='Los Angeles International Airport',
            city='Los Angeles',
            country='USA'
        )
        self.assertEqual(airport.code, 'LAX')
        self.assertEqual(str(airport), 'LAX - Los Angeles International Airport')

class AirlineModelTest(TestCase):
    def test_create_airline(self):
        airline = Airline.objects.create(
            code='AA',
            name='American Airlines'
        )
        self.assertEqual(airline.code, 'AA')
        self.assertEqual(str(airline), 'AA - American Airlines')

class FlightModelTest(TestCase):
    def setUp(self):
        self.airline = Airline.objects.create(code='AA', name='American Airlines')
        self.departure_airport = Airport.objects.create(
            code='LAX', name='LAX Airport', city='Los Angeles', country='USA'
        )
        self.arrival_airport = Airport.objects.create(
            code='JFK', name='JFK Airport', city='New York', country='USA'
        )

    def test_create_flight(self):
        departure_time = timezone.now() + timedelta(days=1)
        arrival_time = departure_time + timedelta(hours=5)
        
        flight = Flight.objects.create(
            flight_number='AA100',
            airline=self.airline,
            departure_airport=self.departure_airport,
            arrival_airport=self.arrival_airport,
            departure_time=departure_time,
            arrival_time=arrival_time,
            duration=timedelta(hours=5),
            aircraft_type='Boeing 737',
            economy_price=299.99,
            economy_seats=150,
            available_economy_seats=150
        )
        self.assertEqual(flight.flight_number, 'AA100')
        self.assertEqual(flight.economy_price, 299.99)

class FlightAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)
        
        self.airline = Airline.objects.create(code='AA', name='American Airlines')
        self.departure_airport = Airport.objects.create(
            code='LAX', name='LAX Airport', city='Los Angeles', country='USA'
        )
        self.arrival_airport = Airport.objects.create(
            code='JFK', name='JFK Airport', city='New York', country='USA'
        )
        
        departure_time = timezone.now() + timedelta(days=1)
        arrival_time = departure_time + timedelta(hours=5)
        
        self.flight = Flight.objects.create(
            flight_number='AA100',
            airline=self.airline,
            departure_airport=self.departure_airport,
            arrival_airport=self.arrival_airport,
            departure_time=departure_time,
            arrival_time=arrival_time,
            duration=timedelta(hours=5),
            aircraft_type='Boeing 737',
            economy_price=299.99,
            economy_seats=150,
            available_economy_seats=150
        )

    def test_airport_list(self):
        url = reverse('airport-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_flight_search(self):
        url = reverse('search-flights')
        params = {
            'departure_airport': 'LAX',
            'arrival_airport': 'JFK',
            'departure_date': (timezone.now() + timedelta(days=1)).date(),
            'passengers': 1,
            'travel_class': 'economy'
        }
        response = self.client.get(url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('outbound_flights', response.data)

    def test_flight_booking_creation(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        url = reverse('flight-booking-list')
        
        booking_data = {
            'flight_id': self.flight.id,
            'passenger_count': 2,
            'travel_class': 'economy'
        }
        response = self.client.post(url, booking_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check if seats were reduced
        self.flight.refresh_from_db()
        self.assertEqual(self.flight.available_economy_seats, 148)

    def test_flight_booking_list(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
        # Create a booking first
        FlightBooking.objects.create(
            user=self.user,
            flight=self.flight,
            booking_reference='TEST123',
            passenger_count=1,
            travel_class='economy',
            total_price=299.99
        )
        
        url = reverse('flight-booking-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_insufficient_seats_booking(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
        # Try to book more seats than available
        self.flight.available_economy_seats = 1
        self.flight.save()
        
        url = reverse('flight-booking-list')
        booking_data = {
            'flight_id': self.flight.id,
            'passenger_count': 5,
            'travel_class': 'economy'
        }
        response = self.client.post(url, booking_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)