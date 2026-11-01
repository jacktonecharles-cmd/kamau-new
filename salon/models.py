from django.db import models
from django.utils import timezone
from django.db import models

class Service(models.Model):
    id = models.BigAutoField(primary_key=True)
    # ... your other fields


class ServiceCategory(models.Model):
    """Groups services e.g. Manicure, Pedicure, Nail Art."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = 'Service categories'

    def __str__(self):
        return self.name


class Service(models.Model):
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    duration_minutes = models.PositiveIntegerField(default=45)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image_url = models.URLField(
        help_text="Link to a service photo. Placeholder photos are fine during development."
    )
    is_featured = models.BooleanField(default=False)

    class Meta:
        ordering = ['category__order', 'name']

    def __str__(self):
        return self.name


class Technician(models.Model):
    name = models.CharField(max_length=120)
    position = models.CharField(max_length=120, default='Nail Technician')
    years_experience = models.PositiveIntegerField(default=1)
    specialties = models.CharField(max_length=255, help_text="Comma-separated, e.g. Nail Art, Acrylics")
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=5.0)
    photo_url = models.URLField()
    bio = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

    def specialty_list(self):
        return [s.strip() for s in self.specialties.split(',') if s.strip()]

    def __str__(self):
        return self.name


class GalleryCategory(models.TextChoices):
    ACRYLIC = 'acrylic', 'Acrylic Nails'
    GEL = 'gel', 'Gel Nails'
    ART = 'art', 'Nail Art'
    FRENCH = 'french', 'French Tips'
    BRIDAL = 'bridal', 'Bridal Nails'
    PEDICURE = 'pedicure', 'Pedicures'
    BEFORE_AFTER = 'before_after', 'Before & After'


class GalleryImage(models.Model):
    title = models.CharField(max_length=150)
    category = models.CharField(max_length=20, choices=GalleryCategory.choices)
    image_url = models.URLField()

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.title


class Testimonial(models.Model):
    client_name = models.CharField(max_length=120)
    rating = models.PositiveSmallIntegerField(default=5)
    quote = models.TextField()
    photo_url = models.URLField(blank=True)
    is_published = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.client_name} ({self.rating} stars)"


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='bookings')
    technician = models.ForeignKey(
        Technician, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='bookings', help_text="Leave blank for 'no preference'."
    )
    date = models.DateField()
    time = models.TimeField()
    special_requests = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} - {self.service.name} on {self.date}"


class PaymentProof(models.Model):
    """Manual payment verification workflow (send money -> upload proof -> admin approves)."""
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payment_proofs', null=True, blank=True)
    customer_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=30)
    service_name = models.CharField(max_length=150)
    amount_paid = models.DecimalField(max_digits=8, decimal_places=2)
    transaction_code = models.CharField(max_length=100)
    screenshot = models.ImageField(upload_to='payment_proofs/')
    is_verified = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.customer_name} - {self.amount_paid} ({self.transaction_code})"


class ContactMessage(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    message = models.TextField()
    submitted_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"Message from {self.name}"


class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.email
