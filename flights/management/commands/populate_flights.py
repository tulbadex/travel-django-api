from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from flights.models import Airport, Airline, Flight
import random

class Command(BaseCommand):
    help = 'Populate database with sample flights'

    def handle(self, *args, **options):
        # Create airports
        airports_data = [
            {'code': 'LAX', 'name': 'Los Angeles International Airport', 'city': 'Los Angeles', 'country': 'USA'},
            {'code': 'JFK', 'name': 'John F. Kennedy International Airport', 'city': 'New York', 'country': 'USA'},
            {'code': 'LHR', 'name': 'London Heathrow Airport', 'city': 'London', 'country': 'UK'},
            {'code': 'CDG', 'name': 'Charles de Gaulle Airport', 'city': 'Paris', 'country': 'France'},
            {'code': 'DXB', 'name': 'Dubai International Airport', 'city': 'Dubai', 'country': 'UAE'},
            {'code': 'NRT', 'name': 'Narita International Airport', 'city': 'Tokyo', 'country': 'Japan'},
            {'code': 'SIN', 'name': 'Singapore Changi Airport', 'city': 'Singapore', 'country': 'Singapore'},
            {'code': 'SYD', 'name': 'Sydney Kingsford Smith Airport', 'city': 'Sydney', 'country': 'Australia'},
            {'code': 'ORD', 'name': 'Chicago O\'Hare International Airport', 'city': 'Chicago', 'country': 'USA'},
            {'code': 'ATL', 'name': 'Hartsfield-Jackson Atlanta International Airport', 'city': 'Atlanta', 'country': 'USA'},
            {'code': 'FRA', 'name': 'Frankfurt Airport', 'city': 'Frankfurt', 'country': 'Germany'},
            {'code': 'AMS', 'name': 'Amsterdam Airport Schiphol', 'city': 'Amsterdam', 'country': 'Netherlands'},
            {'code': 'MAD', 'name': 'Madrid-Barajas Airport', 'city': 'Madrid', 'country': 'Spain'},
            {'code': 'FCO', 'name': 'Leonardo da Vinci International Airport', 'city': 'Rome', 'country': 'Italy'},
            {'code': 'YYZ', 'name': 'Toronto Pearson International Airport', 'city': 'Toronto', 'country': 'Canada'},
            {'code': 'MEX', 'name': 'Mexico City International Airport', 'city': 'Mexico City', 'country': 'Mexico'},
            {'code': 'GRU', 'name': 'São Paulo/Guarulhos International Airport', 'city': 'São Paulo', 'country': 'Brazil'},
            {'code': 'JNB', 'name': 'O.R. Tambo International Airport', 'city': 'Johannesburg', 'country': 'South Africa'},
            {'code': 'CAI', 'name': 'Cairo International Airport', 'city': 'Cairo', 'country': 'Egypt'},
            {'code': 'BOM', 'name': 'Chhatrapati Shivaji Maharaj International Airport', 'city': 'Mumbai', 'country': 'India'},
        ]

        for airport_data in airports_data:
            Airport.objects.get_or_create(**airport_data)

        # Create airlines
        airlines_data = [
            {'code': 'AA', 'name': 'American Airlines'},
            {'code': 'BA', 'name': 'British Airways'},
            {'code': 'EK', 'name': 'Emirates'},
            {'code': 'SQ', 'name': 'Singapore Airlines'},
            {'code': 'QF', 'name': 'Qantas'},
        ]

        for airline_data in airlines_data:
            Airline.objects.get_or_create(**airline_data)

        # Create flights
        airports = list(Airport.objects.all())
        airlines = list(Airline.objects.all())
        
        # Generate multiple flights per route for better coverage
        route_combinations = [(dep, arr) for dep in airports for arr in airports if dep != arr]
        
        for route in route_combinations:
            departure_airport, arrival_airport = route
            
            # Generate 3-5 flights per route across different dates
            flights_per_route = random.randint(3, 5)
            
            for j in range(flights_per_route):
                airline = random.choice(airlines)
                
                # Ensure flights are distributed across next 90 days for better search results
                base_date = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
                days_ahead = random.randint(0, 90)  # Next 3 months
                hour = random.randint(6, 22)
                minute = random.choice([0, 15, 30, 45])
                
                departure_time = base_date + timedelta(days=days_ahead, hours=hour, minutes=minute)
                flight_duration = timedelta(hours=random.randint(2, 15), minutes=random.randint(0, 59))
                arrival_time = departure_time + flight_duration
            
            flight_number = f"{airline.code}{random.randint(100, 999)}"
            
            # Ensure unique flight number for this airline and date
            while Flight.objects.filter(
                flight_number=flight_number,
                airline=airline,
                departure_time__date=departure_time.date()
            ).exists():
                flight_number = f"{airline.code}{random.randint(100, 999)}"
            
            Flight.objects.get_or_create(
                flight_number=flight_number,
                airline=airline,
                departure_time=departure_time,
                defaults={
                    'departure_airport': departure_airport,
                    'arrival_airport': arrival_airport,
                    'arrival_time': arrival_time,
                    'duration': flight_duration,
                    'aircraft_type': random.choice(['Boeing 737', 'Airbus A320', 'Boeing 777', 'Airbus A350']),
                    'economy_price': random.randint(200, 800),
                    'business_price': random.randint(800, 2000),
                    'first_class_price': random.randint(2000, 5000),
                    'economy_seats': random.randint(100, 300),
                    'business_seats': random.randint(10, 50),
                    'first_class_seats': random.randint(5, 20),
                    'available_economy_seats': random.randint(50, 200),
                    'available_business_seats': random.randint(10, 50),
                    'available_first_class_seats': random.randint(5, 20),
                    'status': 'scheduled'
                }
            )

        self.stdout.write(self.style.SUCCESS('Successfully populated flights'))