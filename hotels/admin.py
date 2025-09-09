from django.contrib import admin
from django.utils.html import format_html
from .models import Destination, HotelCategory, Hotel

@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'is_popular', 'created_at')
    list_filter = ('country', 'is_popular', 'created_at')
    search_fields = ('name', 'country', 'description')
    ordering = ('name',)
    list_editable = ('is_popular',)
    
    fieldsets = (
        (None, {'fields': ('name', 'country')}),
        ('Details', {'fields': ('description', 'image')}),
        ('Status', {'fields': ('is_popular',)}),
        ('Timestamps', {'fields': ('created_at',), 'classes': ('collapse',)}),
    )
    readonly_fields = ('created_at',)

@admin.register(HotelCategory)
class HotelCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)
    
    fieldsets = (
        (None, {'fields': ('name',)}),
        ('Details', {'fields': ('description',)}),
        ('Timestamps', {'fields': ('created_at',), 'classes': ('collapse',)}),
    )
    readonly_fields = ('created_at',)

@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ('name', 'destination', 'star_rating', 'price_per_night', 'is_featured')
    list_filter = ('destination', 'star_rating', 'is_featured')
    search_fields = ('name', 'description', 'destination__name')
    ordering = ('-created_at',)
    list_editable = ('is_featured',)
    
    fieldsets = (
        (None, {'fields': ('name', 'destination')}),
        ('Details', {'fields': ('description', 'address', 'star_rating')}),
        ('Pricing & Capacity', {'fields': ('price_per_night', 'total_rooms', 'available_rooms')}),
        ('Location', {'fields': ('latitude', 'longitude')}),
        ('Media', {'fields': ('main_image',)}),
        ('Relations', {'fields': ('amenities',)}),
        ('Status', {'fields': ('is_featured',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('amenities',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('destination')