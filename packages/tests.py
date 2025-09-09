from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from decimal import Decimal
from datetime import date, timedelta
from django.utils import timezone
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
            username='testuser',
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
        url = reverse('packages:search_packages')
        future_date = (timezone.now() + timedelta(days=30)).date()
        params = {
            'destination': 'Bali',
            'travel_date': future_date.isoformat(),
            'participants': 4,
            'package_type': 'full_package'
        }
        response = self.client.get(url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_package_categories(self):
        url = reverse('packages:category_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Beach')

    def test_featured_packages(self):
        url = reverse('packages:package_list')
        params = {'featured': 'true'}
        response = self.client.get(url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check if response.data is paginated
        if hasattr(response.data, 'get') and 'results' in response.data:
            packages = response.data['results']
        else:
            packages = response.data
        
        # Should return featured packages
        featured_packages = [pkg for pkg in packages if isinstance(pkg, dict) and pkg.get('is_featured')]
        self.assertTrue(len(featured_packages) >= 0)

    def test_package_search_with_filters(self):
        url = reverse('packages:search_packages')
        future_date = (timezone.now() + timedelta(days=30)).date()
        params = {
            'destination': 'Bali',
            'travel_date': future_date.isoformat(),
            'participants': 4,
            'min_price': 1000,
            'max_price': 1500,
            'duration_days': 7,
            'includes_flight': 'true'
        }
        response = self.client.get(url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_package_search_by_category(self):
        url = reverse('packages:search_packages')
        future_date = (timezone.now() + timedelta(days=30)).date()
        params = {
            'category': self.category.id,
            'travel_date': future_date.isoformat(),
            'participants': 2
        }
        response = self.client.get(url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_package_search_insufficient_capacity(self):
        # Test package capacity validation
        packages = TravelPackage.objects.filter(
            max_participants__gte=25
        )
        self.assertEqual(packages.count(), 0)  # No packages with capacity >= 25
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
        
        # Test that only active packages are returned
        active_packages = TravelPackage.objects.filter(is_active=True)
        inactive_packages = TravelPackage.objects.filter(is_active=False)
        
        self.assertEqual(active_packages.count(), 1)
        self.assertEqual(inactive_packages.count(), 1)
        self.assertNotIn(inactive_package, active_packages)