from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q

from .models import PackageCategory, TravelPackage, PackageBooking, PackageReview
from .serializers import (
    PackageCategorySerializer,
    TravelPackageSerializer,
    TravelPackageListSerializer,
    PackageSearchSerializer,
    PackageBookingSerializer,
    PackageBookingListSerializer,
    PackageReviewSerializer
)

class PackageCategoryListView(generics.ListAPIView):
    queryset = PackageCategory.objects.all().order_by('name')
    serializer_class = PackageCategorySerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

class TravelPackageListView(generics.ListAPIView):
    serializer_class = TravelPackageListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = TravelPackage.objects.filter(is_active=True)
        featured = self.request.query_params.get('featured', None)
        if featured:
            queryset = queryset.filter(is_featured=True)
        return queryset

class TravelPackageDetailView(generics.RetrieveAPIView):
    queryset = TravelPackage.objects.filter(is_active=True)
    serializer_class = TravelPackageSerializer
    permission_classes = [permissions.AllowAny]

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def search_packages(request):
    serializer = PackageSearchSerializer(data=request.query_params)
    if serializer.is_valid():
        data = serializer.validated_data
        
        queryset = TravelPackage.objects.filter(is_active=True)
        
        # Filter by destination
        if data.get('destination'):
            queryset = queryset.filter(
                Q(destination__name__icontains=data['destination']) |
                Q(destination__country__icontains=data['destination']) |
                Q(name__icontains=data['destination'])
            )
        
        # Filter by category
        if data.get('category'):
            queryset = queryset.filter(category__name__icontains=data['category'])
        
        # Filter by package type
        if data.get('package_type'):
            queryset = queryset.filter(package_type=data['package_type'])
        
        # Filter by price range
        if data.get('min_price'):
            queryset = queryset.filter(price_per_person__gte=data['min_price'])
        if data.get('max_price'):
            queryset = queryset.filter(price_per_person__lte=data['max_price'])
        
        # Filter by duration
        if data.get('duration_days'):
            queryset = queryset.filter(duration_days=data['duration_days'])
        
        # Check availability (simplified - in production, check actual bookings)
        participants = data['participants']
        queryset = queryset.filter(max_participants__gte=participants)
        
        packages = TravelPackageListSerializer(queryset, many=True).data
        
        # Add calculated total price for the group
        for package in packages:
            package['total_price_for_group'] = float(package['price_per_person']) * participants
        
        return Response({
            'packages': packages,
            'search_params': {
                'travel_date': data['travel_date'],
                'participants': participants
            }
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PackageBookingCreateView(generics.CreateAPIView):
    serializer_class = PackageBookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Check package availability
        package = TravelPackage.objects.get(id=serializer.validated_data['package_id'])
        participants = serializer.validated_data['participants']
        
        if participants > package.max_participants:
            return Response({'error': f'Maximum {package.max_participants} participants allowed'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        if participants < package.min_participants:
            return Response({'error': f'Minimum {package.min_participants} participants required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        booking = serializer.save()
        
        return Response(PackageBookingSerializer(booking).data, status=status.HTTP_201_CREATED)

class PackageBookingListView(generics.ListAPIView):
    serializer_class = PackageBookingListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PackageBooking.objects.filter(user=self.request.user).order_by('-created_at')

class PackageBookingDetailView(generics.RetrieveAPIView):
    serializer_class = PackageBookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PackageBooking.objects.filter(user=self.request.user)

class PackageReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = PackageReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        package_id = self.kwargs['package_id']
        return PackageReview.objects.filter(package_id=package_id).order_by('-created_at')

    def perform_create(self, serializer):
        package_id = self.kwargs['package_id']
        serializer.save(user=self.request.user, package_id=package_id)