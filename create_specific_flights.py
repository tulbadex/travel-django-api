import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_api.settings')
django.setup()

from flights.models import Flight, Airport, Airline
from datetime import datetime, timedelta
from django.utils import timezone

# Get airports and airlines
bom = Airport.objects.get(code='BOM')
nrt = Airport.objects.get(code='NRT')
airline = Airline.objects.first()

# Create flights for the next 30 days for BOM-NRT route
base_date = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)

for i in range(30):
    flight_date = base_date + timedelta(days=i)
    
    # Create morning flight
    departure_time = flight_date + timedelta(hours=8, minutes=30)
    arrival_time = departure_time + timedelta(hours=7, minutes=45)
    
    Flight.objects.get_or_create(
        flight_number=f"AI{100+i}",
        airline=airline,
        departure_time=departure_time,
        defaults={
            'departure_airport': bom,
            'arrival_airport': nrt,
            'arrival_time': arrival_time,
            'duration': timedelta(hours=7, minutes=45),
            'aircraft_type': 'Boeing 777',
            'economy_price': 650,
            'business_price': 1200,
            'first_class_price': 2500,
            'economy_seats': 200,
            'business_seats': 30,
            'first_class_seats': 12,
            'available_economy_seats': 180,
            'available_business_seats': 25,
            'available_first_class_seats': 10,
            'status': 'scheduled'
        }
    )
    
    # Create evening flight
    departure_time = flight_date + timedelta(hours=18, minutes=15)
    arrival_time = departure_time + timedelta(hours=7, minutes=30)
    
    Flight.objects.get_or_create(
        flight_number=f"SQ{200+i}",
        airline=airline,
        departure_time=departure_time,
        defaults={
            'departure_airport': bom,
            'arrival_airport': nrt,
            'arrival_time': arrival_time,
            'duration': timedelta(hours=7, minutes=30),
            'aircraft_type': 'Airbus A350',
            'economy_price': 680,
            'business_price': 1350,
            'first_class_price': 2800,
            'economy_seats': 180,
            'business_seats': 28,
            'first_class_seats': 10,
            'available_economy_seats': 160,
            'available_business_seats': 22,
            'available_first_class_seats': 8,
            'status': 'scheduled'
        }
    )

print("Created specific BOM-NRT flights for next 30 days")