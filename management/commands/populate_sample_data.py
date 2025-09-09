from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from flights.models import Airport, Airline, Flight
from hotels.models import Destination, Amenity, Hotel
from packages.models import PackageCategory, TravelPackage
from datetime import datetime, timedelta
from decimal import Decimal

User = get_user_model()

class Command(BaseCommand):
    help = 'Populate database with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create airports
        airports_data = [
            {'code': 'JFK', 'name': 'John F. Kennedy International Airport', 'city': 'New York', 'country': 'USA'},
            {'code': 'LAX', 'name': 'Los Angeles International Airport', 'city': 'Los Angeles', 'country': 'USA'},
            {'code': 'LHR', 'name': 'London Heathrow Airport', 'city': 'London', 'country': 'UK'},
            {'code': 'CDG', 'name': 'Charles de Gaulle Airport', 'city': 'Paris', 'country': 'France'},
            {'code': 'NRT', 'name': 'Narita International Airport', 'city': 'Tokyo', 'country': 'Japan'},
        ]
        
        for airport_data in airports_data:
            Airport.objects.get_or_create(**airport_data)
        
        # Create airlines
        airlines_data = [
            {'code': 'AA', 'name': 'American Airlines'},
            {'code': 'BA', 'name': 'British Airways'},
            {'code': 'AF', 'name': 'Air France'},
            {'code': 'JL', 'name': 'Japan Airlines'},
        ]
        
        for airline_data in airlines_data:
            Airline.objects.get_or_create(**airline_data)
        
        # Create sample flights
        aa = Airline.objects.get(code='AA')
        jfk = Airport.objects.get(code='JFK')
        lax = Airport.objects.get(code='LAX')
        
        Flight.objects.get_or_create(
            flight_number='100',
            airline=aa,
            departure_airport=jfk,
            arrival_airport=lax,
            departure_time=datetime.now() + timedelta(days=7, hours=8),
            arrival_time=datetime.now() + timedelta(days=7, hours=14),
            duration=timedelta(hours=6),
            aircraft_type='Boeing 737',
            economy_price=Decimal('299.99'),
            business_price=Decimal('899.99'),
            economy_seats=150,
            business_seats=20,
            available_economy_seats=150,
            available_business_seats=20
        )
        
        # Create destinations
        destinations_data = [
            {'name': 'New York', 'country': 'USA', 'description': 'The city that never sleeps', 'is_popular': True},
            {'name': 'Paris', 'country': 'France', 'description': 'City of lights and romance', 'is_popular': True},
            {'name': 'Tokyo', 'country': 'Japan', 'description': 'Modern metropolis with ancient traditions', 'is_popular': True},
            {'name': 'London', 'country': 'UK', 'description': 'Historic capital with royal heritage', 'is_popular': True},
        ]
        
        for dest_data in destinations_data:
            Destination.objects.get_or_create(**dest_data)
        
        # Create amenities
        amenities_data = [
            {'name': 'WiFi', 'icon': 'fas fa-wifi'},
            {'name': 'Pool', 'icon': 'fas fa-swimming-pool'},
            {'name': 'Gym', 'icon': 'fas fa-dumbbell'},
            {'name': 'Spa', 'icon': 'fas fa-spa'},
            {'name': 'Restaurant', 'icon': 'fas fa-utensils'},
        ]
        
        for amenity_data in amenities_data:
            Amenity.objects.get_or_create(**amenity_data)
        
        # Create sample hotels
        ny_dest = Destination.objects.get(name='New York')
        wifi = Amenity.objects.get(name='WiFi')
        pool = Amenity.objects.get(name='Pool')
        
        hotel, created = Hotel.objects.get_or_create(
            name='Grand Hotel New York',
            destination=ny_dest,
            address='123 Broadway, New York, NY',
            description='Luxury hotel in the heart of Manhattan',
            star_rating=5,
            price_per_night=Decimal('299.99'),
            total_rooms=200,
            available_rooms=150,
            is_featured=True
        )
        if created:
            hotel.amenities.add(wifi, pool)
        
        # Create package categories
        categories_data = [
            {'name': 'Adventure', 'description': 'Thrilling outdoor experiences'},
            {'name': 'Romance', 'description': 'Perfect for couples'},
            {'name': 'Family', 'description': 'Fun for the whole family'},
            {'name': 'Cultural', 'description': 'Explore local culture and history'},
        ]
        
        for cat_data in categories_data:
            PackageCategory.objects.get_or_create(**cat_data)
        
        # Create sample packages
        adventure_cat = PackageCategory.objects.get(name='Adventure')
        paris_dest = Destination.objects.get(name='Paris')
        
        TravelPackage.objects.get_or_create(
            name='Paris Adventure Package',
            category=adventure_cat,
            destination=paris_dest,
            description='Explore the best of Paris with guided tours and activities',
            package_type='full_package',
            duration_days=5,
            duration_nights=4,
            price_per_person=Decimal('1299.99'),
            max_participants=20,
            min_participants=2,
            includes_flight=True,
            includes_hotel=True,
            includes_meals=True,
            includes_transport=True,
            includes_activities=True,
            is_featured=True
        )
        
        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))