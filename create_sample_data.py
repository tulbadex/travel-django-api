#!/usr/bin/env python
import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_api.settings')
django.setup()

from packages.models import PackageCategory, TravelPackage
from hotels.models import Destination, HotelCategory

def create_sample_data():
    print("Creating sample data...")
    
    # Create destinations
    destinations = [
        {'name': 'Paris', 'country': 'France', 'description': 'City of Light'},
        {'name': 'Tokyo', 'country': 'Japan', 'description': 'Modern metropolis'},
        {'name': 'New York', 'country': 'USA', 'description': 'The Big Apple'},
        {'name': 'London', 'country': 'UK', 'description': 'Historic capital'},
        {'name': 'Dubai', 'country': 'UAE', 'description': 'Luxury destination'},
        {'name': 'Bali', 'country': 'Indonesia', 'description': 'Tropical paradise'},
        {'name': 'Rome', 'country': 'Italy', 'description': 'Eternal city'},
        {'name': 'Bangkok', 'country': 'Thailand', 'description': 'Cultural hub'},
    ]
    
    for dest_data in destinations:
        destination, created = Destination.objects.get_or_create(
            name=dest_data['name'],
            defaults=dest_data
        )
        if created:
            print(f"Created destination: {destination.name}")
    
    # Create package categories
    categories = [
        {'name': 'Adventure', 'description': 'Thrilling outdoor experiences'},
        {'name': 'Cultural', 'description': 'Immerse in local culture'},
        {'name': 'Beach', 'description': 'Relaxing beach getaways'},
        {'name': 'City Break', 'description': 'Urban exploration'},
        {'name': 'Honeymoon', 'description': 'Romantic escapes'},
        {'name': 'Family', 'description': 'Fun for all ages'},
        {'name': 'Luxury', 'description': 'Premium experiences'},
        {'name': 'Budget', 'description': 'Affordable travel'},
    ]
    
    for cat_data in categories:
        category, created = PackageCategory.objects.get_or_create(
            name=cat_data['name'],
            defaults=cat_data
        )
        if created:
            print(f"Created category: {category.name}")
    
    # Create hotel categories
    hotel_categories = [
        {'name': 'Business', 'description': 'Professional accommodations'},
        {'name': 'Luxury', 'description': 'Premium hotel experience'},
        {'name': 'Budget', 'description': 'Affordable stays'},
        {'name': 'Boutique', 'description': 'Unique design hotels'},
        {'name': 'Resort', 'description': 'All-inclusive resorts'},
    ]
    
    for cat_data in hotel_categories:
        category, created = HotelCategory.objects.get_or_create(
            name=cat_data['name'],
            defaults=cat_data
        )
        if created:
            print(f"Created hotel category: {category.name}")
    
    # Create travel packages
    packages = [
        {
            'name': 'Paris City Explorer',
            'category': 'City Break',
            'destination': 'Paris',
            'description': 'Discover the magic of Paris with guided tours',
            'package_type': 'flight_hotel',
            'duration_days': 5,
            'duration_nights': 4,
            'price_per_person': Decimal('1200.00'),
            'max_participants': 20,
            'min_participants': 2,
            'includes_flight': True,
            'includes_hotel': True,
            'includes_meals': False,
            'includes_transport': True,
            'is_featured': True,
        },
        {
            'name': 'Tokyo Adventure',
            'category': 'Cultural',
            'destination': 'Tokyo',
            'description': 'Experience traditional and modern Japan',
            'package_type': 'full_package',
            'duration_days': 7,
            'duration_nights': 6,
            'price_per_person': Decimal('2500.00'),
            'max_participants': 15,
            'min_participants': 1,
            'includes_flight': True,
            'includes_hotel': True,
            'includes_meals': True,
            'includes_transport': True,
            'is_featured': True,
        },
        {
            'name': 'Bali Beach Retreat',
            'category': 'Beach',
            'destination': 'Bali',
            'description': 'Relax on pristine beaches with spa treatments',
            'package_type': 'hotel_only',
            'duration_days': 6,
            'duration_nights': 5,
            'price_per_person': Decimal('800.00'),
            'max_participants': 25,
            'min_participants': 2,
            'includes_flight': False,
            'includes_hotel': True,
            'includes_meals': True,
            'includes_transport': False,
            'is_featured': False,
        },
        {
            'name': 'Dubai Luxury Experience',
            'category': 'Luxury',
            'destination': 'Dubai',
            'description': 'Ultimate luxury in the desert metropolis',
            'package_type': 'full_package',
            'duration_days': 4,
            'duration_nights': 3,
            'price_per_person': Decimal('3500.00'),
            'max_participants': 10,
            'min_participants': 2,
            'includes_flight': True,
            'includes_hotel': True,
            'includes_meals': True,
            'includes_transport': True,
            'is_featured': True,
        },
        {
            'name': 'Rome Historical Tour',
            'category': 'Cultural',
            'destination': 'Rome',
            'description': 'Walk through ancient history',
            'package_type': 'flight_hotel',
            'duration_days': 4,
            'duration_nights': 3,
            'price_per_person': Decimal('950.00'),
            'max_participants': 30,
            'min_participants': 1,
            'includes_flight': True,
            'includes_hotel': True,
            'includes_meals': False,
            'includes_transport': True,
            'is_featured': False,
        },
        {
            'name': 'New York City Break',
            'category': 'City Break',
            'destination': 'New York',
            'description': 'The city that never sleeps',
            'package_type': 'flight_hotel',
            'duration_days': 5,
            'duration_nights': 4,
            'price_per_person': Decimal('1800.00'),
            'max_participants': 20,
            'min_participants': 1,
            'includes_flight': True,
            'includes_hotel': True,
            'includes_meals': False,
            'includes_transport': False,
            'is_featured': True,
        },
    ]
    
    for pkg_data in packages:
        try:
            category = PackageCategory.objects.get(name=pkg_data['category'])
            destination = Destination.objects.get(name=pkg_data['destination'])
            
            package, created = TravelPackage.objects.get_or_create(
                name=pkg_data['name'],
                defaults={
                    **pkg_data,
                    'category': category,
                    'destination': destination,
                }
            )
            if created:
                print(f"Created package: {package.name}")
        except Exception as e:
            print(f"Error creating package {pkg_data['name']}: {e}")
    
    print("Sample data creation completed!")

if __name__ == '__main__':
    create_sample_data()