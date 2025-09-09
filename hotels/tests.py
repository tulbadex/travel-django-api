from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from decimal import Decimal
from .models import Destination, HotelCategory, Hotel, Amenity

User = get_user_model()

class DestinationModelTest(TestCase):
    def test_create_destination(self):
        destination = Destination.objects.create(
            name='Paris',
            country='France',
            description='City of Light',
            is_popular=True
        )
        self.assertEqual(destination.name, 'Paris')
        self.assertEqual(str(destination), 'Paris, France')
        self.assertTrue(destination.is_popular)

class HotelCategoryModelTest(TestCase):
    def test_create_hotel_category(self):
        category = HotelCategory.objects.create(
            name='Luxury',
            description='High-end luxury hotels'
        )
        self.assertEqual(category.name, 'Luxury')
        self.assertEqual(str(category), 'Luxury')

class AmenityModelTest(TestCase):
    def test_create_amenity(self):
        amenity = Amenity.objects.create(
            name='WiFi',
            icon='fas fa-wifi'
        )
        self.assertEqual(amenity.name, 'WiFi')
        self.assertEqual(str(amenity), 'WiFi')

class HotelModelTest(TestCase):
    def setUp(self):
        self.destination = Destination.objects.create(
            name='Paris',
            country='France',
            description='City of Light'
        )
        self.amenity = Amenity.objects.create(name='WiFi')

    def test_create_hotel(self):
        hotel = Hotel.objects.create(
            name='Grand Hotel Paris',
            destination=self.destination,
            address='123 Champs Elysees',
            description='Luxury hotel in Paris',
            star_rating=5,
            price_per_night=Decimal('299.99'),
            total_rooms=100,
            available_rooms=95,
            is_featured=True
        )
        hotel.amenities.add(self.amenity)
        
        self.assertEqual(hotel.name, 'Grand Hotel Paris')
        self.assertEqual(hotel.star_rating, 5)
        self.assertEqual(hotel.price_per_night, Decimal('299.99'))
        self.assertTrue(hotel.is_featured)
        self.assertIn(self.amenity, hotel.amenities.all())

class HotelAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)
        
        self.destination = Destination.objects.create(
            name='Paris',
            country='France',
            description='City of Light'
        )
        
        self.category = HotelCategory.objects.create(
            name='Luxury',
            description='Luxury hotels'
        )
        
        self.amenity = Amenity.objects.create(name='WiFi')
        
        self.hotel = Hotel.objects.create(
            name='Grand Hotel Paris',
            destination=self.destination,
            address='123 Champs Elysees',
            description='Luxury hotel in Paris',
            star_rating=5,
            price_per_night=Decimal('299.99'),
            total_rooms=100,
            available_rooms=95,
            is_featured=True
        )
        self.hotel.amenities.add(self.amenity)

    def test_hotel_search(self):
        url = reverse('hotel-search')
        params = {
            'destination': 'Paris',
            'check_in': '2024-12-01',
            'check_out': '2024-12-05',
            'guests': 2,
            'rooms': 1
        }
        response = self.client.get(url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_hotel_categories(self):
        url = reverse('hotel-categories')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Luxury')

    def test_featured_hotels(self):
        url = reverse('hotel-list')
        params = {'featured': 'true'}
        response = self.client.get(url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should return featured hotels
        featured_hotels = [hotel for hotel in response.data if hotel.get('is_featured')]
        self.assertTrue(len(featured_hotels) > 0)

    def test_hotel_search_with_filters(self):
        url = reverse('hotel-search')
        params = {
            'destination': 'Paris',
            'check_in': '2024-12-01',
            'check_out': '2024-12-05',
            'guests': 2,
            'rooms': 1,
            'min_price': 200,
            'max_price': 400,
            'star_rating': 5
        }
        response = self.client.get(url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_hotel_search_no_results(self):
        url = reverse('hotel-search')
        params = {
            'destination': 'NonExistentCity',
            'check_in': '2024-12-01',
            'check_out': '2024-12-05',
            'guests': 2,
            'rooms': 1
        }
        response = self.client.get(url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return empty results or handle gracefully

    def test_invalid_date_range(self):
        url = reverse('hotel-search')
        params = {
            'destination': 'Paris',
            'check_in': '2024-12-05',  # Check-in after check-out
            'check_out': '2024-12-01',
            'guests': 2,
            'rooms': 1
        }
        response = self.client.get(url, params)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)