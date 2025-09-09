from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from decimal import Decimal
from datetime import date
from .models import Booking, BookingItem
from hotels.models import Hotel, Destination
from flights.models import Flight, Airline, Airport
from packages.models import TravelPackage, PackageCategory
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class BookingModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_create_booking(self):
        booking = Booking.objects.create(
            booking_reference='BK123456',
            user=self.user,
            status='pending',
            travel_date=date(2024, 12, 1),
            total_amount=Decimal('999.99'),
            contact_email='test@example.com',
            contact_phone='+1234567890'
        )
        
        self.assertEqual(booking.booking_reference, 'BK123456')
        self.assertEqual(booking.user, self.user)
        self.assertEqual(booking.status, 'pending')
        self.assertEqual(booking.total_amount, Decimal('999.99'))
        self.assertEqual(str(booking), 'Booking BK123456')

class BookingItemModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.booking = Booking.objects.create(
            booking_reference='BK123456',
            user=self.user,
            travel_date=date(2024, 12, 1),
            total_amount=Decimal('999.99'),
            contact_email='test@example.com',
            contact_phone='+1234567890'
        )
        
        # Create a hotel for testing
        self.destination = Destination.objects.create(
            name='Paris',
            country='France',
            description='City of Light'
        )
        
        self.hotel = Hotel.objects.create(
            name='Test Hotel',
            destination=self.destination,
            address='123 Test St',
            description='Test hotel',
            star_rating=4,
            price_per_night=Decimal('199.99'),
            total_rooms=100,
            available_rooms=95
        )

    def test_create_booking_item_with_hotel(self):
        hotel_content_type = ContentType.objects.get_for_model(Hotel)
        
        booking_item = BookingItem.objects.create(
            booking=self.booking,
            content_type=hotel_content_type,
            object_id=self.hotel.id,
            quantity=2,
            price=Decimal('399.98')
        )
        
        self.assertEqual(booking_item.booking, self.booking)
        self.assertEqual(booking_item.content_object, self.hotel)
        self.assertEqual(booking_item.quantity, 2)
        self.assertEqual(booking_item.price, Decimal('399.98'))

class BookingIntegrationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test data for different booking types
        self.destination = Destination.objects.create(
            name='Paris',
            country='France',
            description='City of Light'
        )
        
        # Hotel
        self.hotel = Hotel.objects.create(
            name='Test Hotel',
            destination=self.destination,
            address='123 Test St',
            description='Test hotel',
            star_rating=4,
            price_per_night=Decimal('199.99'),
            total_rooms=100,
            available_rooms=95
        )
        
        # Flight
        self.airline = Airline.objects.create(code='AA', name='American Airlines')
        self.departure_airport = Airport.objects.create(
            code='LAX', name='LAX Airport', city='Los Angeles', country='USA'
        )
        self.arrival_airport = Airport.objects.create(
            code='CDG', name='CDG Airport', city='Paris', country='France'
        )
        
        departure_time = timezone.now() + timedelta(days=30)
        arrival_time = departure_time + timedelta(hours=11)
        
        self.flight = Flight.objects.create(
            flight_number='AA100',
            airline=self.airline,
            departure_airport=self.departure_airport,
            arrival_airport=self.arrival_airport,
            departure_time=departure_time,
            arrival_time=arrival_time,
            duration=timedelta(hours=11),
            aircraft_type='Boeing 777',
            economy_price=Decimal('599.99'),
            economy_seats=200,
            available_economy_seats=200
        )
        
        # Package
        self.category = PackageCategory.objects.create(
            name='City Break',
            description='City break packages'
        )
        
        self.package = TravelPackage.objects.create(
            name='Paris City Break',
            category=self.category,
            destination=self.destination,
            description='3 days in Paris',
            package_type='full_package',
            duration_days=3,
            duration_nights=2,
            price_per_person=Decimal('799.99'),
            max_participants=10,
            includes_flight=True,
            includes_hotel=True
        )

    def test_multi_item_booking(self):
        # Create a booking with multiple items
        booking = Booking.objects.create(
            booking_reference='BK789012',
            user=self.user,
            travel_date=date(2024, 12, 1),
            total_amount=Decimal('1599.97'),
            contact_email='test@example.com',
            contact_phone='+1234567890'
        )
        
        # Add hotel booking item
        hotel_content_type = ContentType.objects.get_for_model(Hotel)
        BookingItem.objects.create(
            booking=booking,
            content_type=hotel_content_type,
            object_id=self.hotel.id,
            quantity=2,  # 2 nights
            price=Decimal('399.98')
        )
        
        # Add flight booking item
        flight_content_type = ContentType.objects.get_for_model(Flight)
        BookingItem.objects.create(
            booking=booking,
            content_type=flight_content_type,
            object_id=self.flight.id,
            quantity=1,  # 1 flight
            price=Decimal('599.99')
        )
        
        # Add package booking item
        package_content_type = ContentType.objects.get_for_model(TravelPackage)
        BookingItem.objects.create(
            booking=booking,
            content_type=package_content_type,
            object_id=self.package.id,
            quantity=1,  # 1 package
            price=Decimal('799.99')
        )
        
        # Verify booking has all items
        self.assertEqual(booking.items.count(), 3)
        
        # Verify total calculation (manual check)
        total_items_price = sum(item.price for item in booking.items.all())
        self.assertEqual(total_items_price, Decimal('1799.96'))

    def test_booking_status_transitions(self):
        booking = Booking.objects.create(
            booking_reference='BK345678',
            user=self.user,
            status='pending',
            travel_date=date(2024, 12, 1),
            total_amount=Decimal('999.99'),
            contact_email='test@example.com',
            contact_phone='+1234567890'
        )
        
        # Test status transitions
        self.assertEqual(booking.status, 'pending')
        
        booking.status = 'confirmed'
        booking.save()
        self.assertEqual(booking.status, 'confirmed')
        
        booking.status = 'completed'
        booking.save()
        self.assertEqual(booking.status, 'completed')

    def test_booking_with_special_requests(self):
        booking = Booking.objects.create(
            booking_reference='BK567890',
            user=self.user,
            travel_date=date(2024, 12, 1),
            total_amount=Decimal('999.99'),
            contact_email='test@example.com',
            contact_phone='+1234567890',
            special_requests='Vegetarian meals, late check-in',
            notes='Customer prefers ground floor room'
        )
        
        self.assertEqual(booking.special_requests, 'Vegetarian meals, late check-in')
        self.assertEqual(booking.notes, 'Customer prefers ground floor room')