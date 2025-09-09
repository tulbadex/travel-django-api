from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q
from datetime import datetime
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import uuid

from .models import Airport, Airline, Flight, FlightBooking
from .serializers import (
    AirportSerializer, 
    AirlineSerializer, 
    FlightSerializer,
    FlightSearchSerializer,
    FlightBookingSerializer,
    FlightBookingListSerializer
)

# Sample airports data
SAMPLE_AIRPORTS = [
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
]

class AirportListView(generics.ListAPIView):
    serializer_class = AirportSerializer
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        search = request.query_params.get('search', '')
        
        # Try to get from database first
        queryset = Airport.objects.all()
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(city__icontains=search) | 
                Q(code__icontains=search)
            )
        
        # If no airports in database, return sample data
        if not queryset.exists():
            airports_data = SAMPLE_AIRPORTS
            if search:
                airports_data = [
                    airport for airport in SAMPLE_AIRPORTS
                    if search.lower() in airport['name'].lower() or 
                       search.lower() in airport['city'].lower() or 
                       search.lower() in airport['code'].lower()
                ]
            return Response(airports_data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class AirlineListView(generics.ListAPIView):
    queryset = Airline.objects.all()
    serializer_class = AirlineSerializer
    permission_classes = [permissions.AllowAny]

@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter('departure_airport', openapi.IN_QUERY, description="Departure airport code", type=openapi.TYPE_STRING, required=True),
        openapi.Parameter('arrival_airport', openapi.IN_QUERY, description="Arrival airport code", type=openapi.TYPE_STRING, required=True),
        openapi.Parameter('departure_date', openapi.IN_QUERY, description="Departure date (YYYY-MM-DD)", type=openapi.TYPE_STRING, required=True),
        openapi.Parameter('return_date', openapi.IN_QUERY, description="Return date (YYYY-MM-DD)", type=openapi.TYPE_STRING, required=False),
        openapi.Parameter('passengers', openapi.IN_QUERY, description="Number of passengers", type=openapi.TYPE_INTEGER, default=1),
        openapi.Parameter('travel_class', openapi.IN_QUERY, description="Travel class", type=openapi.TYPE_STRING, enum=['economy', 'business', 'first'], default='economy'),
    ],
    responses={200: FlightSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def search_flights(request):
    serializer = FlightSearchSerializer(data=request.query_params)
    if serializer.is_valid():
        data = serializer.validated_data
        
        # Search outbound flights
        outbound_flights = Flight.objects.filter(
            departure_airport__code=data['departure_airport'],
            arrival_airport__code=data['arrival_airport'],
            departure_time__date=data['departure_date'],
            status='scheduled'
        ).select_related('airline', 'departure_airport', 'arrival_airport')
        
        # Filter by available seats based on travel class
        travel_class = data['travel_class']
        passengers = data['passengers']
        
        if travel_class == 'economy':
            outbound_flights = outbound_flights.filter(available_economy_seats__gte=passengers)
        elif travel_class == 'business':
            outbound_flights = outbound_flights.filter(available_business_seats__gte=passengers)
        elif travel_class == 'first':
            outbound_flights = outbound_flights.filter(available_first_class_seats__gte=passengers)
        
        result = {
            'outbound_flights': FlightSerializer(outbound_flights, many=True).data,
            'return_flights': []
        }
        
        # Search return flights if return date provided
        if data.get('return_date'):
            return_flights = Flight.objects.filter(
                departure_airport__code=data['arrival_airport'],
                arrival_airport__code=data['departure_airport'],
                departure_time__date=data['return_date'],
                status='scheduled'
            ).select_related('airline', 'departure_airport', 'arrival_airport')
            
            if travel_class == 'economy':
                return_flights = return_flights.filter(available_economy_seats__gte=passengers)
            elif travel_class == 'business':
                return_flights = return_flights.filter(available_business_seats__gte=passengers)
            elif travel_class == 'first':
                return_flights = return_flights.filter(available_first_class_seats__gte=passengers)
            
            result['return_flights'] = FlightSerializer(return_flights, many=True).data
        
        return Response(result)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FlightBookingListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return FlightBookingSerializer
        return FlightBookingListSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return FlightBooking.objects.none()
        return FlightBooking.objects.filter(user=self.request.user).order_by('-created_at')
    
    @swagger_auto_schema(
        operation_description="Create a new flight booking",
        request_body=FlightBookingSerializer,
        responses={201: FlightBookingSerializer, 400: 'Validation errors'}
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="List user's flight bookings",
        responses={200: FlightBookingListSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Check flight availability
        flight = Flight.objects.get(id=serializer.validated_data['flight_id'])
        travel_class = serializer.validated_data['travel_class']
        passenger_count = serializer.validated_data['passenger_count']
        
        # Check available seats
        if travel_class == 'economy' and flight.available_economy_seats < passenger_count:
            return Response({'error': 'Not enough economy seats available'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        elif travel_class == 'business' and flight.available_business_seats < passenger_count:
            return Response({'error': 'Not enough business seats available'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        elif travel_class == 'first' and flight.available_first_class_seats < passenger_count:
            return Response({'error': 'Not enough first class seats available'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Create booking using serializer
        booking = serializer.save()
        
        # Update available seats
        if travel_class == 'economy':
            flight.available_economy_seats -= passenger_count
        elif travel_class == 'business':
            flight.available_business_seats -= passenger_count
        else:
            flight.available_first_class_seats -= passenger_count
        flight.save()
        
        return Response(FlightBookingSerializer(booking).data, status=status.HTTP_201_CREATED)

class FlightBookingDetailView(generics.RetrieveAPIView):
    serializer_class = FlightBookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return FlightBooking.objects.none()
        return FlightBooking.objects.filter(user=self.request.user)