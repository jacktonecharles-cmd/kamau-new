from django import forms
from .models import Booking, PaymentProof, ContactMessage, NewsletterSubscriber


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = [
            'full_name', 'email', 'phone', 'service',
            'technician', 'date', 'time', 'special_requests',
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': 'Your full name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'you@example.com'}),
            'phone': forms.TextInput(attrs={'placeholder': '07XX XXX XXX'}),
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'special_requests': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Anything we should know? (optional)'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['technician'].required = False
        self.fields['technician'].empty_label = "No preference"


class PaymentProofForm(forms.ModelForm):
    class Meta:
        model = PaymentProof
        fields = [
            'customer_name', 'phone', 'service_name',
            'amount_paid', 'transaction_code', 'screenshot',
        ]
        widgets = {
            'customer_name': forms.TextInput(attrs={'placeholder': 'Your full name'}),
            'phone': forms.TextInput(attrs={'placeholder': '07XX XXX XXX'}),
            'service_name': forms.TextInput(attrs={'placeholder': 'e.g. Luxury Gel Manicure'}),
            'transaction_code': forms.TextInput(attrs={'placeholder': 'M-Pesa transaction code'}),
        }


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 5, 'placeholder': 'How can we help?'}),
        }


class NewsletterForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscriber
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'Your email address'}),
        }
