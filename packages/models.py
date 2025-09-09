from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from hotels.models import Hotel, Destination
from flights.models import Flight

User = get_user_model()

class PackageCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Package Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

class TravelPackage(models.Model):
    PACKAGE_TYPE = [
        ('flight_hotel', 'Flight + Hotel'),
        ('hotel_only', 'Hotel Only'),
        ('flight_only', 'Flight Only'),
        ('full_package', 'Full Package'),
    ]

    name = models.CharField(max_length=200)
    category = models.ForeignKey(PackageCategory, on_delete=models.CASCADE)
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE)
    description = models.TextField()
    package_type = models.CharField(max_length=20, choices=PACKAGE_TYPE)
    duration_days = models.PositiveIntegerField()
    duration_nights = models.PositiveIntegerField()
    price_per_person = models.DecimalField(max_digits=10, decimal_places=2)
    max_participants = models.PositiveIntegerField()
    min_participants = models.PositiveIntegerField(default=1)
    main_image = models.ImageField(upload_to='packages/', null=True, blank=True)
    includes_flight = models.BooleanField(default=False)
    includes_hotel = models.BooleanField(default=False)
    includes_meals = models.BooleanField(default=False)
    includes_transport = models.BooleanField(default=False)
    includes_activities = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews:
            return sum([review.rating for review in reviews]) / len(reviews)
        return 0

class PackageImage(models.Model):
    package = models.ForeignKey(TravelPackage, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='packages/gallery/')
    caption = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.package.name} - Image"

class PackageItinerary(models.Model):
    package = models.ForeignKey(TravelPackage, on_delete=models.CASCADE, related_name='itinerary')
    day_number = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    description = models.TextField()
    activities = models.TextField(blank=True)
    meals_included = models.CharField(max_length=100, blank=True)

    class Meta:
        unique_together = ['package', 'day_number']
        ordering = ['day_number']

    def __str__(self):
        return f"{self.package.name} - Day {self.day_number}"

class PackageBooking(models.Model):
    BOOKING_STATUS = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    package = models.ForeignKey(TravelPackage, on_delete=models.CASCADE)
    booking_reference = models.CharField(max_length=10, unique=True)
    travel_date = models.DateField()
    participants = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(20)])
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=BOOKING_STATUS, default='pending')
    special_requests = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Booking {self.booking_reference} - {self.package.name}"

class PackageParticipant(models.Model):
    booking = models.ForeignKey(PackageBooking, on_delete=models.CASCADE, related_name='participants_details')
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    passport_number = models.CharField(max_length=20, blank=True)
    dietary_requirements = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class PackageReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    package = models.ForeignKey(TravelPackage, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=200)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'package']

    def __str__(self):
        return f"{self.package.name} - {self.rating} stars by {self.user.email}"
