from django.contrib import admin
from .models import (
    ServiceCategory, Service, Technician, GalleryImage,
    Testimonial, Booking, PaymentProof, ContactMessage, NewsletterSubscriber,
)


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'duration_minutes', 'is_featured')
    list_filter = ('category', 'is_featured')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Technician)
class TechnicianAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'years_experience', 'rating')
    search_fields = ('name', 'specialties')


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'category')
    list_filter = ('category',)


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'rating', 'is_published')
    list_filter = ('is_published', 'rating')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'service', 'technician', 'date', 'time', 'status', 'created_at')
    list_filter = ('status', 'date', 'service')
    search_fields = ('full_name', 'email', 'phone')
    list_editable = ('status',)
    date_hierarchy = 'date'


@admin.register(PaymentProof)
class PaymentProofAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'service_name', 'amount_paid', 'transaction_code', 'is_verified', 'submitted_at')
    list_filter = ('is_verified',)
    list_editable = ('is_verified',)
    search_fields = ('customer_name', 'transaction_code', 'phone')


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'submitted_at')
    readonly_fields = ('submitted_at',)


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'subscribed_at')
