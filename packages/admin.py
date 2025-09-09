from django.contrib import admin
from django.utils.html import format_html
from .models import PackageCategory, TravelPackage

@admin.register(PackageCategory)
class PackageCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)
    
    fieldsets = (
        (None, {'fields': ('name',)}),
        ('Details', {'fields': ('description', 'icon')}),
        ('Timestamps', {'fields': ('created_at',), 'classes': ('collapse',)}),
    )
    readonly_fields = ('created_at',)

@admin.register(TravelPackage)
class TravelPackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'destination', 'category', 'package_type', 'price_per_person', 'duration_display', 'is_featured', 'is_active')
    list_filter = ('category', 'destination', 'package_type', 'is_featured', 'is_active', 'includes_flight', 'includes_hotel')
    search_fields = ('name', 'description', 'destination__name')
    ordering = ('-created_at',)
    list_editable = ('is_featured', 'is_active')
    
    fieldsets = (
        (None, {'fields': ('name', 'destination', 'category', 'package_type')}),
        ('Details', {'fields': ('description',)}),
        ('Duration & Capacity', {'fields': ('duration_days', 'duration_nights', 'min_participants', 'max_participants')}),
        ('Pricing', {'fields': ('price_per_person',)}),
        ('Inclusions', {'fields': ('includes_flight', 'includes_hotel', 'includes_meals', 'includes_transport')}),
        ('Media', {'fields': ('image_url',)}),
        ('Status', {'fields': ('is_featured', 'is_active')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    readonly_fields = ('created_at', 'updated_at')
    
    def duration_display(self, obj):
        return f"{obj.duration_days}D/{obj.duration_nights}N"
    duration_display.short_description = 'Duration'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('destination', 'category')