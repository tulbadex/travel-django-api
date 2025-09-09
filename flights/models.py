from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()

class Airport(models.Model):
    code = models.CharField(max_length=3, unique=True)  # IATA code
    name = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    timezone = models.CharField(max_length=50, default='UTC')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

class Airline(models.Model):
    code = models.CharField(max_length=3, unique=True)  # IATA code
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='airlines/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

class Flight(models.Model):
    FLIGHT_STATUS = [
        ('scheduled', 'Scheduled'),
        ('delayed', 'Delayed'),
        ('cancelled', 'Cancelled'),
        ('boarding', 'Boarding'),
        ('departed', 'Departed'),
        ('arrived', 'Arrived'),
    ]

    flight_number = models.CharField(max_length=10)
    airline = models.ForeignKey(Airline, on_delete=models.CASCADE)
    departure_airport = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='departing_flights')
    arrival_airport = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='arriving_flights')
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    duration = models.DurationField()
    aircraft_type = models.CharField(max_length=50)
    economy_price = models.DecimalField(max_digits=10, decimal_places=2)
    business_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    first_class_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    economy_seats = models.PositiveIntegerField()
    business_seats = models.PositiveIntegerField(default=0)
    first_class_seats = models.PositiveIntegerField(default=0)
    available_economy_seats = models.PositiveIntegerField()
    available_business_seats = models.PositiveIntegerField(default=0)
    available_first_class_seats = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=FLIGHT_STATUS, default='scheduled')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['flight_number', 'airline', 'departure_time']

    def __str__(self):
        return f"{self.airline.code}{self.flight_number} - {self.departure_airport.code} to {self.arrival_airport.code}"

class FlightBooking(models.Model):
    BOOKING_STATUS = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    CLASS_CHOICES = [
        ('economy', 'Economy'),
        ('business', 'Business'),
        ('first', 'First Class'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    booking_reference = models.CharField(max_length=10, unique=True)
    passenger_count = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(9)])
    travel_class = models.CharField(max_length=10, choices=CLASS_CHOICES, default='economy')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=BOOKING_STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Booking {self.booking_reference} - {self.user.email}"

class Passenger(models.Model):
    booking = models.ForeignKey(FlightBooking, on_delete=models.CASCADE, related_name='passengers')
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    passport_number = models.CharField(max_length=20, blank=True)
    seat_number = models.CharField(max_length=5, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
