from rest_framework import serializers
from .models import Airport, Airline, Flight, FlightBooking, Passenger
import uuid

class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = '__all__'

class AirlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airline
        fields = '__all__'

class FlightSerializer(serializers.ModelSerializer):
    airline = AirlineSerializer(read_only=True)
    departure_airport = AirportSerializer(read_only=True)
    arrival_airport = AirportSerializer(read_only=True)
    
    class Meta:
        model = Flight
        fields = '__all__'

class FlightSearchSerializer(serializers.Serializer):
    departure_airport = serializers.CharField(max_length=3)
    arrival_airport = serializers.CharField(max_length=3)
    departure_date = serializers.DateField()
    return_date = serializers.DateField(required=False)
    passengers = serializers.IntegerField(min_value=1, max_value=9, default=1)
    travel_class = serializers.ChoiceField(
        choices=['economy', 'business', 'first'],
        default='economy'
    )

class PassengerSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True, required=False)
    phone = serializers.CharField(max_length=20, write_only=True, required=False)
    date_of_birth = serializers.DateField(required=True)
    passport_number = serializers.CharField(required=True)
    
    class Meta:
        model = Passenger
        fields = ['first_name', 'last_name', 'email', 'phone', 'date_of_birth', 'passport_number']

class FlightBookingSerializer(serializers.ModelSerializer):
    passengers = PassengerSerializer(many=True)
    flight = FlightSerializer(read_only=True)
    flight_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = FlightBooking
        fields = ['id', 'flight', 'flight_id', 'booking_reference', 'passenger_count', 
                 'travel_class', 'total_price', 'status', 'passengers', 'created_at']
        read_only_fields = ['id', 'booking_reference', 'total_price', 'status', 'created_at']

    def create(self, validated_data):
        passengers_data = validated_data.pop('passengers')
        flight = Flight.objects.get(id=validated_data['flight_id'])
        
        # Calculate total price
        travel_class = validated_data['travel_class']
        passenger_count = validated_data['passenger_count']
        
        if travel_class == 'economy':
            price_per_person = flight.economy_price
        elif travel_class == 'business':
            price_per_person = flight.business_price
        else:
            price_per_person = flight.first_class_price
        
        validated_data['user'] = self.context['request'].user
        validated_data['booking_reference'] = str(uuid.uuid4())[:10].upper()
        validated_data['total_price'] = price_per_person * passenger_count
        validated_data['flight'] = flight
        
        # Remove flight_id as we're using flight object
        validated_data.pop('flight_id')
        
        booking = FlightBooking.objects.create(**validated_data)
        
        for passenger_data in passengers_data:
            Passenger.objects.create(
                booking=booking,
                first_name=passenger_data['first_name'],
                last_name=passenger_data['last_name'],
                date_of_birth=passenger_data['date_of_birth'],
                passport_number=passenger_data['passport_number']
            )
        
        return booking

class FlightBookingListSerializer(serializers.ModelSerializer):
    flight = FlightSerializer(read_only=True)
    
    class Meta:
        model = FlightBooking
        fields = ['id', 'flight', 'booking_reference', 'passenger_count', 
                 'travel_class', 'total_price', 'status', 'created_at']