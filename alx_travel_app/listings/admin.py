from django.contrib import admin
from .models import Listing, Booking, Review, Payment

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'price_per_night', 'host', 'created_at')
    search_fields = ('name', 'location', 'description')
    list_filter = ('created_at', 'location')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('property', 'user', 'start_date', 'end_date', 'total_price', 'status')
    search_fields = ('property__name', 'user__email')
    list_filter = ('status', 'start_date', 'end_date')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('property', 'user', 'rating', 'created_at')
    search_fields = ('property__name', 'user__email', 'comment')
    list_filter = ('rating', 'created_at')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('booking', 'amount', 'currency', 'status', 'created_at')
    search_fields = ('booking__property__name', 'chapa_transaction_ref')
    list_filter = ('status', 'currency', 'created_at')
