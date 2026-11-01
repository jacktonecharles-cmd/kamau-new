from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404

from .forms import BookingForm, PaymentProofForm, ContactForm, NewsletterForm
from .models import (
    Service, ServiceCategory, Technician, GalleryImage,
    Testimonial, Booking,
)


def home(request):
    context = {
        'featured_services': Service.objects.filter(is_featured=True)[:6],
        'technicians': Technician.objects.all()[:3],
        'testimonials': Testimonial.objects.filter(is_published=True)[:6],
        'gallery_preview': GalleryImage.objects.all()[:15],
        'newsletter_form': NewsletterForm(),
    }
    return render(request, 'salon/home.html', context)


def about(request):
    return render(request, 'salon/about.html', {'technicians': Technician.objects.all()})


def services(request):
    categories = ServiceCategory.objects.prefetch_related('services').all()
    return render(request, 'salon/services.html', {'categories': categories})


def service_detail(request, slug):
    service = get_object_or_404(Service, slug=slug)
    related = Service.objects.filter(category=service.category).exclude(pk=service.pk)[:3]
    return render(request, 'salon/service_detail.html', {'service': service, 'related': related})


def team(request):
    return render(request, 'salon/team.html', {'technicians': Technician.objects.all()})


def gallery(request):
    category = request.GET.get('category', 'all')
    images = GalleryImage.objects.all()
    if category != 'all':
        images = images.filter(category=category)
    return render(request, 'salon/gallery.html', {
        'images': images,
        'active_category': category,
        'categories': GalleryImage._meta.get_field('category').choices,
    })


def booking(request):
    initial = {}
    service_slug = request.GET.get('service')
    if service_slug:
        service_obj = Service.objects.filter(slug=service_slug).first()
        if service_obj:
            initial['service'] = service_obj

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            new_booking = form.save()
            send_mail(
                subject=f"Booking confirmed: {new_booking.service.name}",
                message=(
                    f"Hi {new_booking.full_name},\n\n"
                    f"Your appointment for {new_booking.service.name} on "
                    f"{new_booking.date} at {new_booking.time} has been received "
                    f"and is now pending confirmation. We'll be in touch shortly.\n\n"
                    f"Kamau Nails\nPhone: {settings.SALON_PHONE}"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[new_booking.email, settings.SALON_ADMIN_EMAIL],
                fail_silently=True,
            )
            return redirect('booking_success')
    else:
        form = BookingForm(initial=initial)

    return render(request, 'salon/booking.html', {'form': form})


def booking_success(request):
    return render(request, 'salon/booking_success.html')


def payment(request):
    if request.method == 'POST':
        form = PaymentProofForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Thank you! Your payment proof has been submitted and is awaiting verification."
            )
            return redirect('payment')
    else:
        form = PaymentProofForm()

    return render(request, 'salon/payment.html', {
        'form': form,
        'payment_number': settings.SALON_PHONE,
    })


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your message has been sent. We'll reply within 24 hours.")
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'salon/contact.html', {'form': form})


def newsletter_signup(request):
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "You're subscribed! Watch your inbox for promotions.")
        else:
            messages.error(request, "That email didn't work — please try again.")
    return redirect(request.META.get('HTTP_REFERER', 'home'))


def faq(request):
    return render(request, 'salon/faq.html')


def policy(request, slug):
    policies = {
        'cancellation': 'Cancellation Policy',
        'no-show': 'No-Show Policy',
        'refund': 'Refund Policy',
        'privacy': 'Privacy Policy',
        'terms': 'Terms & Conditions',
        'health-safety': 'Health & Safety Policy',
        'children': 'Children Policy',
        'tipping': 'Tipping Information',
    }
    title = policies.get(slug)
    if not title:
        title = 'Policy Not Found'
    return render(request, 'salon/policy.html', {'title': title, 'slug': slug})
