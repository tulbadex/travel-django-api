from rest_framework import serializers
from .models import Destination, Amenity, Hotel, HotelImage, HotelBooking, HotelReview, HotelCategory
import uuid
from datetime import datetime

class HotelCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = HotelCategory
        fields = ['id', 'name', 'description']

class DestinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Destination
        fields = '__all__'

class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = '__all__'

class HotelImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = HotelImage
        fields = ['id', 'image', 'caption']

class HotelReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = HotelReview
        fields = ['id', 'user_name', 'rating', 'title', 'comment', 'created_at']

class HotelSerializer(serializers.ModelSerializer):
    destination = DestinationSerializer(read_only=True)
    amenities = AmenitySerializer(many=True, read_only=True)
    images = HotelImageSerializer(many=True, read_only=True)
    reviews = HotelReviewSerializer(many=True, read_only=True)
    average_rating = serializers.ReadOnlyField()
    
    class Meta:
        model = Hotel
        fields = '__all__'

class HotelListSerializer(serializers.ModelSerializer):
    destination = DestinationSerializer(read_only=True)
    average_rating = serializers.ReadOnlyField()
    
    class Meta:
        model = Hotel
        fields = ['id', 'name', 'destination', 'star_rating', 'main_image', 
                 'price_per_night', 'average_rating', 'is_featured']

class HotelSearchSerializer(serializers.Serializer):
    destination = serializers.CharField(required=False)
    check_in_date = serializers.DateField()
    check_out_date = serializers.DateField()
    guests = serializers.IntegerField(min_value=1, max_value=10, default=1)
    rooms = serializers.IntegerField(min_value=1, max_value=5, default=1)
    min_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    max_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    star_rating = serializers.IntegerField(min_value=1, max_value=5, required=False)

    def validate(self, data):
        if data['check_out_date'] <= data['check_in_date']:
            raise serializers.ValidationError("Check-out date must be after check-in date")
        
        if data['check_in_date'] < datetime.now().date():
            raise serializers.ValidationError("Check-in date cannot be in the past")
        
        return data

class HotelBookingSerializer(serializers.ModelSerializer):
    hotel = HotelSerializer(read_only=True)
    hotel_id = serializers.IntegerField(write_only=True)
    nights = serializers.ReadOnlyField()
    
    class Meta:
        model = HotelBooking
        fields = ['id', 'hotel', 'hotel_id', 'booking_reference', 'check_in_date', 
                 'check_out_date', 'nights', 'guests', 'rooms', 'total_price', 
                 'status', 'special_requests', 'created_at']
        read_only_fields = ['id', 'booking_reference', 'status', 'created_at']

    def validate(self, data):
        if data['check_out_date'] <= data['check_in_date']:
            raise serializers.ValidationError("Check-out date must be after check-in date")
        
        if data['check_in_date'] < datetime.now().date():
            raise serializers.ValidationError("Check-in date cannot be in the past")
        
        return data

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        validated_data['booking_reference'] = str(uuid.uuid4())[:10].upper()
        
        # Calculate nights and total price
        check_in = validated_data['check_in_date']
        check_out = validated_data['check_out_date']
        nights = (check_out - check_in).days
        
        hotel = Hotel.objects.get(id=validated_data['hotel_id'])
        total_price = hotel.price_per_night * nights * validated_data['rooms']
        
        validated_data['nights'] = nights
        validated_data['total_price'] = total_price
        
        return super().create(validated_data)

class HotelBookingListSerializer(serializers.ModelSerializer):
    hotel = HotelListSerializer(read_only=True)
    
    class Meta:
        model = HotelBooking
        fields = ['id', 'hotel', 'booking_reference', 'check_in_date', 
                 'check_out_date', 'nights', 'guests', 'rooms', 'total_price', 
                 'status', 'created_at']