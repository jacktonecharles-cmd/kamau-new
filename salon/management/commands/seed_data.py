from django.core.management.base import BaseCommand
from salon.models import (
    ServiceCategory, Service, Technician, GalleryImage,
    GalleryCategory, Testimonial,
)


class Command(BaseCommand):
    help = "Populate the database with sample Kamau Nails content (services, team, gallery, testimonials)."

    def handle(self, *args, **options):
        self.stdout.write("Seeding Kamau Nails sample data...")

        categories_data = [
            ("Manicure", "manicure", [
                ("Classic Manicure", 800, 30, "A refreshing classic manicure with shaping, cuticle care and polish.",
                 "https://images.unsplash.com/photo-1604654894610-df63bc536371?w=800&q=80", True),
                ("Luxury Manicure", 1800, 60, "An indulgent manicure with exfoliation, hot towel wrap and hand massage.",
                 "https://images.unsplash.com/photo-1610992015732-2449b2f5cf14?w=800&q=80", True),
                ("Gel Manicure", 1500, 45, "Long-lasting gel polish manicure with a high-gloss, chip-resistant finish.",
                 "https://images.unsplash.com/photo-1610992015732-2449b2f5cf14?w=800&q=80", False),
            ]),
            ("Pedicure", "pedicure", [
                ("Classic Pedicure", 1000, 40, "Soothing soak, shaping and polish for healthy, happy feet.",
                 "https://images.unsplash.com/photo-1519014816548-bf5fe059798b?w=800&q=80", False),
                ("Spa Pedicure", 2000, 60, "Exfoliating scrub, mask and extended massage for total relaxation.",
                 "https://images.unsplash.com/photo-1519014816548-bf5fe059798b?w=800&q=80", True),
                ("Luxury Pedicure", 2800, 75, "Our most indulgent pedicure with paraffin treatment and hot stone massage.",
                 "https://images.unsplash.com/photo-1519014816548-bf5fe059798b?w=800&q=80", False),
            ]),
            ("Nail Extensions", "extensions", [
                ("Acrylic Nails", 2500, 90, "Durable acrylic extensions sculpted and shaped to your preferred length.",
                 "https://images.unsplash.com/photo-1587909209111-5097ee578ec3?w=800&q=80", True),
                ("Gel Nails", 2700, 90, "Lightweight, flexible gel extensions with a natural, glossy finish.",
                 "https://images.unsplash.com/photo-1587909209111-5097ee578ec3?w=800&q=80", False),
            ]),
            ("Nail Art & Finishes", "nail-art", [
                ("Custom Nail Art", 500, 30, "Hand-painted designs, from minimalist lines to full statement art (per set, add-on).",
                 "https://images.unsplash.com/photo-1600334129128-685c5582fd35?w=800&q=80", True),
                ("French Tips", 400, 20, "The timeless classic — clean white tips over a natural or sheer base.",
                 "https://images.unsplash.com/photo-1600334129128-685c5582fd35?w=800&q=80", False),
                ("Ombre Nails", 600, 30, "A seamless gradient blend between two or more polish shades.",
                 "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=800&q=80", False),
                ("Nail Repairs", 300, 15, "Quick, professional fixes for chips, cracks or lifted extensions.",
                 "https://images.unsplash.com/photo-1610992015732-2449b2f5cf14?w=800&q=80", False),
            ]),
            ("Bridal & Kids", "bridal-kids", [
                ("Bridal Package", 5000, 120, "A full pampering package for the bride: manicure, pedicure and delicate nail art.",
                 "https://images.unsplash.com/photo-1519741497674-611481863552?w=800&q=80", True),
                ("Kids Nail Service", 500, 25, "Gentle, fun manicures for our youngest clients using kid-safe polish.",
                 "https://images.unsplash.com/photo-1519014816548-bf5fe059798b?w=800&q=80", False),
            ]),
        ]

        for cat_name, cat_slug, services in categories_data:
            category, _ = ServiceCategory.objects.get_or_create(
                slug=cat_slug, defaults={'name': cat_name}
            )
            for name, price, duration, desc, image_url, featured in services:
                Service.objects.get_or_create(
                    slug=name.lower().replace(' ', '-'),
                    defaults=dict(
                        category=category, name=name, description=desc,
                        duration_minutes=duration, price=price,
                        image_url=image_url, is_featured=featured,
                    )
                )

        technicians = [
            ("Amara Kamau", "Lead Nail Artist", 9, "Nail Art, Acrylics, Bridal", 5.0,
             "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=600&q=80"),
            ("Fatima Noor", "Senior Technician", 6, "Gel Nails, Ombre, French Tips", 4.9,
             "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=600&q=80"),
            ("Grace Wanjiru", "Pedicure Specialist", 5, "Spa Pedicures, Foot Care", 4.8,
             "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=600&q=80"),
            ("Lilian Achieng", "Nail Technician", 3, "Classic Manicures, Kids Services", 4.7,
             "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=600&q=80"),
        ]
        for name, position, years, specialties, rating, photo in technicians:
            Technician.objects.get_or_create(
                name=name, defaults=dict(
                    position=position, years_experience=years,
                    specialties=specialties, rating=rating, photo_url=photo,
                )
            )

        gallery = [
            ("Bold French Tips", GalleryCategory.FRENCH, "https://images.unsplash.com/photo-1610992015732-2449b2f5cf14?w=700&q=80"),
            ("Acrylic Coffin Set", GalleryCategory.ACRYLIC, "https://images.unsplash.com/photo-1587909209111-5097ee578ec3?w=700&q=80"),
            ("Hand-painted Florals", GalleryCategory.ART, "https://images.unsplash.com/photo-1600334129128-685c5582fd35?w=700&q=80"),
            ("Bridal Elegance", GalleryCategory.BRIDAL, "https://images.unsplash.com/photo-1519741497674-611481863552?w=700&q=80"),
            ("Glossy Gel Finish", GalleryCategory.GEL, "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=700&q=80"),
            ("Spa Pedicure Session", GalleryCategory.PEDICURE, "https://images.unsplash.com/photo-1519014816548-bf5fe059798b?w=700&q=80"),
            ("Before & After Repair", GalleryCategory.BEFORE_AFTER, "https://images.unsplash.com/photo-1604654894610-df63bc536371?w=700&q=80"),
            ("Ombre Sunset", GalleryCategory.ART, "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=700&q=80"),
        ]
        for title, category, url in gallery:
            GalleryImage.objects.get_or_create(title=title, defaults=dict(category=category, image_url=url))

        testimonials = [
            ("Wanjiru M.", 5, "Absolutely flawless. My gel set lasted a full month without a single chip!",
             "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=200&q=80"),
            ("Achieng O.", 5, "The hygiene standards here are next level. I finally feel safe getting my nails done.",
             "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=200&q=80"),
            ("Njeri K.", 5, "Booked my bridal package with Kamau Nails and the team exceeded every expectation.",
             "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=200&q=80"),
        ]
        for name, rating, quote, photo in testimonials:
            Testimonial.objects.get_or_create(client_name=name, defaults=dict(rating=rating, quote=quote, photo_url=photo))

        self.stdout.write(self.style.SUCCESS("Sample data seeded successfully."))
