from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q
from datetime import datetime

from .models import Destination, Hotel, HotelBooking, HotelReview, HotelCategory
from .serializers import (
    DestinationSerializer,
    HotelSerializer,
    HotelListSerializer,
    HotelSearchSerializer,
    HotelBookingSerializer,
    HotelBookingListSerializer,
    HotelReviewSerializer,
    HotelCategorySerializer
)

class DestinationListView(generics.ListAPIView):
    queryset = Destination.objects.all()
    serializer_class = DestinationSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = Destination.objects.all()
        popular = self.request.query_params.get('popular', None)
        if popular:
            queryset = queryset.filter(is_popular=True)
        return queryset

class HotelCategoryListView(generics.ListAPIView):
    queryset = HotelCategory.objects.all().order_by('name')
    serializer_class = HotelCategorySerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

class HotelListView(generics.ListAPIView):
    serializer_class = HotelListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = Hotel.objects.all()
        featured = self.request.query_params.get('featured', None)
        if featured:
            queryset = queryset.filter(is_featured=True)
        return queryset

class HotelDetailView(generics.RetrieveAPIView):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer
    permission_classes = [permissions.AllowAny]

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def search_hotels(request):
    serializer = HotelSearchSerializer(data=request.query_params)
    if serializer.is_valid():
        data = serializer.validated_data
        
        queryset = Hotel.objects.all()
        
        # Filter by destination
        if data.get('destination'):
            queryset = queryset.filter(
                Q(destination__name__icontains=data['destination']) |
                Q(destination__country__icontains=data['destination']) |
                Q(name__icontains=data['destination'])
            )
        
        # Filter by availability (simplified - in production, check actual bookings)
        rooms_needed = data['rooms']
        queryset = queryset.filter(available_rooms__gte=rooms_needed)
        
        # Filter by price range
        if data.get('min_price'):
            queryset = queryset.filter(price_per_night__gte=data['min_price'])
        if data.get('max_price'):
            queryset = queryset.filter(price_per_night__lte=data['max_price'])
        
        # Filter by star rating
        if data.get('star_rating'):
            queryset = queryset.filter(star_rating=data['star_rating'])
        
        # Calculate nights for pricing display
        check_in = data['check_in_date']
        check_out = data['check_out_date']
        nights = (check_out - check_in).days
        
        hotels = HotelListSerializer(queryset, many=True).data
        
        # Add calculated total price for the stay
        for hotel in hotels:
            hotel['total_price_for_stay'] = float(hotel['price_per_night']) * nights * rooms_needed
            hotel['nights'] = nights
        
        return Response({
            'hotels': hotels,
            'search_params': {
                'check_in_date': check_in,
                'check_out_date': check_out,
                'nights': nights,
                'guests': data['guests'],
                'rooms': data['rooms']
            }
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class HotelBookingCreateView(generics.CreateAPIView):
    serializer_class = HotelBookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Check hotel availability
        hotel = Hotel.objects.get(id=serializer.validated_data['hotel_id'])
        rooms_needed = serializer.validated_data['rooms']
        
        if hotel.available_rooms < rooms_needed:
            return Response({'error': 'Not enough rooms available'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        booking = serializer.save()
        
        # Update available rooms (simplified - in production, use proper booking system)
        hotel.available_rooms -= rooms_needed
        hotel.save()
        
        return Response(HotelBookingSerializer(booking).data, status=status.HTTP_201_CREATED)

class HotelBookingListView(generics.ListAPIView):
    serializer_class = HotelBookingListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return HotelBooking.objects.filter(user=self.request.user).order_by('-created_at')

class HotelBookingDetailView(generics.RetrieveAPIView):
    serializer_class = HotelBookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return HotelBooking.objects.filter(user=self.request.user)

class HotelReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = HotelReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        hotel_id = self.kwargs['hotel_id']
        return HotelReview.objects.filter(hotel_id=hotel_id).order_by('-created_at')

    def perform_create(self, serializer):
        hotel_id = self.kwargs['hotel_id']
        serializer.save(user=self.request.user, hotel_id=hotel_id)