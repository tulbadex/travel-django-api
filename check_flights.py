import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_api.settings')
django.setup()

from flights.models import Flight
from datetime import date

# Check BOM to NRT flights
bom_nrt_flights = Flight.objects.filter(
    departure_airport__code='BOM', 
    arrival_airport__code='NRT'
)
print(f"Total BOM to NRT flights: {bom_nrt_flights.count()}")

# Check flights for specific date
target_date = date(2025, 9, 30)
flights_on_date = Flight.objects.filter(
    departure_airport__code='BOM',
    arrival_airport__code='NRT', 
    departure_time__date=target_date
)
print(f"Flights on {target_date}: {flights_on_date.count()}")

# Show all BOM-NRT flights with dates
print("\nAll BOM-NRT flights:")
for f in bom_nrt_flights[:5]:
    print(f"{f.flight_number} on {f.departure_time.date()} at {f.departure_time.time()}")

# Check if airports exist
from flights.models import Airport
bom = Airport.objects.filter(code='BOM').first()
nrt = Airport.objects.filter(code='NRT').first()
print(f"\nBOM airport exists: {bom is not None}")
print(f"NRT airport exists: {nrt is not None}")