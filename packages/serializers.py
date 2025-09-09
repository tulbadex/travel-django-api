from rest_framework import serializers
from .models import (
    PackageCategory, TravelPackage, PackageImage, PackageItinerary,
    PackageBooking, PackageParticipant, PackageReview
)
from hotels.serializers import DestinationSerializer
import uuid
from datetime import datetime

class PackageCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageCategory
        fields = '__all__'

class PackageImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageImage
        fields = ['id', 'image', 'caption']

class PackageItinerarySerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageItinerary
        fields = '__all__'

class PackageReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = PackageReview
        fields = ['id', 'user_name', 'rating', 'title', 'comment', 'created_at']

class TravelPackageSerializer(serializers.ModelSerializer):
    category = PackageCategorySerializer(read_only=True)
    destination = DestinationSerializer(read_only=True)
    images = PackageImageSerializer(many=True, read_only=True)
    itinerary = PackageItinerarySerializer(many=True, read_only=True)
    reviews = PackageReviewSerializer(many=True, read_only=True)
    average_rating = serializers.ReadOnlyField()
    
    class Meta:
        model = TravelPackage
        fields = '__all__'

class TravelPackageListSerializer(serializers.ModelSerializer):
    category = PackageCategorySerializer(read_only=True)
    destination = DestinationSerializer(read_only=True)
    average_rating = serializers.ReadOnlyField()
    
    class Meta:
        model = TravelPackage
        fields = ['id', 'name', 'category', 'destination', 'duration_days', 
                 'duration_nights', 'price_per_person', 'main_image', 
                 'average_rating', 'is_featured', 'includes_flight', 
                 'includes_hotel', 'includes_meals', 'includes_transport', 
                 'includes_activities']

class PackageSearchSerializer(serializers.Serializer):
    destination = serializers.CharField(required=False)
    category = serializers.CharField(required=False)
    travel_date = serializers.DateField()
    participants = serializers.IntegerField(min_value=1, max_value=20, default=1)
    min_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    max_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    duration_days = serializers.IntegerField(min_value=1, required=False)
    package_type = serializers.ChoiceField(
        choices=['flight_hotel', 'hotel_only', 'flight_only', 'full_package'],
        required=False
    )

    def validate_travel_date(self, value):
        if value < datetime.now().date():
            raise serializers.ValidationError("Travel date cannot be in the past")
        return value

class PackageParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageParticipant
        fields = ['first_name', 'last_name', 'date_of_birth', 'passport_number', 'dietary_requirements']

class PackageBookingSerializer(serializers.ModelSerializer):
    participants_details = PackageParticipantSerializer(many=True)
    package = TravelPackageSerializer(read_only=True)
    package_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = PackageBooking
        fields = ['id', 'package', 'package_id', 'booking_reference', 'travel_date', 
                 'participants', 'total_price', 'status', 'special_requests', 
                 'participants_details', 'created_at']
        read_only_fields = ['id', 'booking_reference', 'status', 'created_at']

    def validate(self, data):
        if data['travel_date'] < datetime.now().date():
            raise serializers.ValidationError("Travel date cannot be in the past")
        
        if len(data['participants_details']) != data['participants']:
            raise serializers.ValidationError("Number of participant details must match participant count")
        
        return data

    def create(self, validated_data):
        participants_data = validated_data.pop('participants_details')
        validated_data['user'] = self.context['request'].user
        validated_data['booking_reference'] = str(uuid.uuid4())[:10].upper()
        
        # Calculate total price
        package = TravelPackage.objects.get(id=validated_data['package_id'])
        total_price = package.price_per_person * validated_data['participants']
        validated_data['total_price'] = total_price
        
        booking = PackageBooking.objects.create(**validated_data)
        
        for participant_data in participants_data:
            PackageParticipant.objects.create(booking=booking, **participant_data)
        
        return booking

class PackageBookingListSerializer(serializers.ModelSerializer):
    package = TravelPackageListSerializer(read_only=True)
    
    class Meta:
        model = PackageBooking
        fields = ['id', 'package', 'booking_reference', 'travel_date', 
                 'participants', 'total_price', 'status', 'created_at']