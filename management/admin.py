from django.contrib import admin
from django.utils.html import format_html
from .models import Booking, BookingItem

class BookingItemInline(admin.TabularInline):
    model = BookingItem
    extra = 0
    readonly_fields = ('created_at',)
    fields = ('content_type', 'object_id', 'quantity', 'price', 'created_at')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_reference', 'user_email', 'status', 'total_amount', 'booking_date', 'travel_date')
    list_filter = ('status', 'booking_date', 'travel_date')
    search_fields = ('booking_reference', 'user__email', 'user__first_name', 'user__last_name')
    ordering = ('-booking_date',)
    readonly_fields = ('booking_reference', 'created_at', 'updated_at')
    inlines = [BookingItemInline]
    
    fieldsets = (
        (None, {'fields': ('booking_reference', 'user', 'status')}),
        ('Dates', {'fields': ('booking_date', 'travel_date')}),
        ('Financial', {'fields': ('total_amount',)}),
        ('Contact', {'fields': ('contact_email', 'contact_phone')}),
        ('Additional Info', {'fields': ('special_requests', 'notes'), 'classes': ('collapse',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    
    def user_email(self, obj):
        return obj.user.email if obj.user else 'N/A'
    user_email.short_description = 'User Email'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

@admin.register(BookingItem)
class BookingItemAdmin(admin.ModelAdmin):
    list_display = ('booking_reference', 'content_type', 'object_id', 'quantity', 'price', 'created_at')
    list_filter = ('content_type', 'created_at')
    search_fields = ('booking__booking_reference',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    
    def booking_reference(self, obj):
        return obj.booking.booking_reference
    booking_reference.short_description = 'Booking Reference'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('booking', 'content_type')