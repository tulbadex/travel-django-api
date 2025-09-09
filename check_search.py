#!/usr/bin/env python
import os
import sys
import django
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_api.settings')
django.setup()

from packages.models import TravelPackage
from django.db.models import Q

def test_search():
    print("Testing package search...")
    
    # Test the exact search parameters
    queryset = TravelPackage.objects.filter(is_active=True)
    
    # Filter by destination (USA)
    usa_packages = queryset.filter(
        Q(destination__name__icontains='USA') |
        Q(destination__country__icontains='USA') |
        Q(name__icontains='USA')
    )
    print(f"USA packages: {usa_packages.count()}")
    
    # Filter by category (Cultural)
    cultural_packages = queryset.filter(category__name__icontains='Cultural')
    print(f"Cultural packages: {cultural_packages.count()}")
    for pkg in cultural_packages:
        print(f"- {pkg.name} ({pkg.destination.name}, {pkg.destination.country})")
    
    # Filter by package type (flight_only)
    flight_only_packages = queryset.filter(package_type='flight_only')
    print(f"Flight only packages: {flight_only_packages.count()}")
    
    # Show all available destinations
    print("\nAll destinations:")
    from hotels.models import Destination
    for dest in Destination.objects.all():
        print(f"- {dest.name}, {dest.country}")
    
    # Show packages that match partial criteria
    print("\nPackages matching 'Cultural' category:")
    cultural_matches = queryset.filter(category__name__icontains='Cultural')
    for pkg in cultural_matches:
        print(f"- {pkg.name}: {pkg.destination.name}, {pkg.destination.country} ({pkg.package_type})")

if __name__ == '__main__':
    test_search()