from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from decimal import Decimal
from datetime import date
from .models import PackageCategory, TravelPackage
from hotels.models import Destination

User = get_user_model()

class PackageCategoryModelTest(TestCase):
    def test_create_package_category(self):
        category = PackageCategory.objects.create(
            name='Adventure',
            description='Adventure travel packages',
            icon='fas fa-mountain'
        )
        self.assertEqual(category.name, 'Adventure')
        self.assertEqual(str(category), 'Adventure')

class TravelPackageModelTest(TestCase):
    def setUp(self):
        self.destination = Destination.objects.create(
            name='Bali',
            country='Indonesia',
            description='Tropical paradise'
        )
        self.category = PackageCategory.objects.create(
            name='Beach',
            description='Beach vacation packages'
        )

    def test_create_travel_package(self):
        package = TravelPackage.objects.create(
            name='Bali Beach Getaway',
            category=self.category,
            destination=self.destination,
            description='7 days in paradise',
            package_type='full_package',
            duration_days=7,
            duration_nights=6,
            price_per_person=Decimal('1299.99'),
            max_participants=20,
            min_participants=2,
            includes_flight=True,
            includes_hotel=True,
            includes_meals=True,
            is_featured=True,
            is_active=True
        )
        
        self.assertEqual(package.name, 'Bali Beach Getaway')
        self.assertEqual(package.duration_days, 7)
        self.assertEqual(package.duration_nights, 6)
        self.assertEqual(package.price_per_person, Decimal('1299.99'))
        self.assertTrue(package.includes_flight)
        self.assertTrue(package.is_featured)

    def test_package_average_rating(self):
        package = TravelPackage.objects.create(
            name='Test Package',
            category=self.category,
            destination=self.destination,
            description='Test package',
            package_type='full_package',
            duration_days=5,
            duration_nights=4,
            price_per_person=Decimal('999.99'),
            max_participants=10
        )
        
        # Test with no reviews
        self.assertEqual(package.average_rating, 0)

class PackageAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)
        
        self.destination = Destination.objects.create(
            name='Bali',
            country='Indonesia',
            description='Tropical paradise'
        )
        
        self.category = PackageCategory.objects.create(
            name='Beach',
            description='Beach vacation packages'
        )
        
        self.package = TravelPackage.objects.create(
            name='Bali Beach Getaway',
            category=self.category,
            destination=self.destination,
            description='7 days in paradise',
            package_type='full_package',
            duration_days=7,
            duration_nights=6,
            price_per_person=Decimal('1299.99'),
            max_participants=20,
            min_participants=2,
            includes_flight=True,
            includes_hotel=True,
            includes_meals=True,
            is_featured=True,
            is_active=True
        )

    def test_package_search(self):
        url = reverse('package-search')
        params = {
            'destination': 'Bali',
            'travel_date': '2024-12-01',
            'participants': 4,
            'package_type': 'full_package'
        }
        response = self.client.get(url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_package_categories(self):
        url = reverse('package-categories')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Beach')

    def test_featured_packages(self):
        url = reverse('package-list')
        params = {'featured': 'true'}
        response = self.client.get(url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should return featured packages
        featured_packages = [pkg for pkg in response.data if pkg.get('is_featured')]
        self.assertTrue(len(featured_packages) > 0)

    def test_package_search_with_filters(self):
        url = reverse('package-search')
        params = {
            'destination': 'Bali',
            'travel_date': '2024-12-01',
            'participants': 4,
            'min_price': 1000,
            'max_price': 1500,
            'duration_days': 7,
            'includes_flight': 'true'
        }
        response = self.client.get(url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_package_search_by_category(self):
        url = reverse('package-search')
        params = {
            'category': self.category.id,
            'travel_date': '2024-12-01',
            'participants': 2
        }
        response = self.client.get(url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_package_search_insufficient_capacity(self):
        url = reverse('package-search')
        params = {
            'destination': 'Bali',
            'travel_date': '2024-12-01',
            'participants': 25  # More than max_participants (20)
        }
        response = self.client.get(url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return empty results or filter out packages with insufficient capacity

    def test_inactive_packages_not_returned(self):
        # Create inactive package
        inactive_package = TravelPackage.objects.create(
            name='Inactive Package',
            category=self.category,
            destination=self.destination,
            description='This package is inactive',
            package_type='full_package',
            duration_days=5,
            duration_nights=4,
            price_per_person=Decimal('999.99'),
            max_participants=10,
            is_active=False  # Inactive
        )
        
        url = reverse('package-search')
        params = {
            'destination': 'Bali',
            'travel_date': '2024-12-01',
            'participants': 2
        }
        response = self.client.get(url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should not include inactive packages
        package_names = [pkg['name'] for pkg in response.data]
        self.assertNotIn('Inactive Package', package_names)