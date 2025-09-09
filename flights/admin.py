from django.contrib import admin
from django.utils.html import format_html
from .models import Airport, Airline, Flight

@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'city', 'country', 'created_at')
    list_filter = ('country', 'created_at')
    search_fields = ('name', 'code', 'city', 'country')
    ordering = ('name',)
    
    fieldsets = (
        (None, {'fields': ('name', 'code')}),
        ('Location', {'fields': ('city', 'country', 'timezone')}),
        ('Timestamps', {'fields': ('created_at',), 'classes': ('collapse',)}),
    )
    readonly_fields = ('created_at',)

@admin.register(Airline)
class AirlineAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'created_at')
    search_fields = ('name', 'code')
    ordering = ('name',)
    
    fieldsets = (
        (None, {'fields': ('name', 'code')}),
        ('Media', {'fields': ('logo',)}),
        ('Timestamps', {'fields': ('created_at',), 'classes': ('collapse',)}),
    )
    readonly_fields = ('created_at',)

@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ('flight_number', 'airline', 'route_display', 'departure_time', 'status')
    list_filter = ('airline', 'departure_airport', 'arrival_airport', 'status', 'departure_time')
    search_fields = ('flight_number', 'airline__name', 'departure_airport__name', 'arrival_airport__name')
    ordering = ('-departure_time',)
    
    fieldsets = (
        (None, {'fields': ('flight_number', 'airline')}),
        ('Route', {'fields': ('departure_airport', 'arrival_airport')}),
        ('Schedule', {'fields': ('departure_time', 'arrival_time', 'duration')}),
        ('Aircraft', {'fields': ('aircraft_type',)}),
        ('Economy Class', {'fields': ('economy_price', 'economy_seats', 'available_economy_seats')}),
        ('Business Class', {'fields': ('business_price', 'business_seats', 'available_business_seats')}),
        ('First Class', {'fields': ('first_class_price', 'first_class_seats', 'available_first_class_seats')}),
        ('Status', {'fields': ('status',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    readonly_fields = ('created_at', 'updated_at')
    
    def route_display(self, obj):
        return f"{obj.departure_airport.code} → {obj.arrival_airport.code}"
    route_display.short_description = 'Route'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('airline', 'departure_airport', 'arrival_airport')