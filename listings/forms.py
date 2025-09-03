# listings/forms.py
from .models import Interest
from django import forms
from .models import Property
from .models import Bid
from .models import Agency
from django.contrib.auth import get_user_model

# This form is used for submitting property images
# It allows multiple file uploads and uses a ClearableFileInput widget for better user experience.
from django import forms

class PropertyImageForm(forms.Form):
    images = forms.FileField(
        required=False,
        label="Upload Property Images",
        
    )


# This form is used for submitting a new property listing
# It includes fields for title, description, price, location, property type, listing type, latitude, longitude, and floor plan.
class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = [
            # Basic Details
            'title', 'description', 'province', 'location', 'latitude', 'longitude',
            'listing_type', 'property_type', 'price', 'area',

            # Property Specs
            'number_of_bedrooms', 'number_of_kitchens', 'number_of_bathrooms',
            'number_of_garages', 'floor_area_m2', 'erf_size_m2',
            'price_per_m2', 'price_per_erf_m2', 'has_parking', 'number_of_parking_slots',
            'unit_no', 'complex_name', 'erf_no', 'ownership_type',
            'township', 'section_number', 'scheme_number', 'scheme_name',

            # Property Features
            'study', 'lounges', 'dining_rooms', 'laundry', 'patio', 'balcony',
            'domestic_accommodation', 'carports', 'flatlet', 'store_room', 'furnished',
            'pool', 'security', 'roof', 'garden', 'views', 'walling', 'flooring',

            # Lease / Rental Details
            'lease_period', 'occupation_date', 'deposit', 'lease_excludes', 'annual_escalation',

            # Mandate / Commission Details
            'mandate_type', 'mandate_start_date', 'mandate_end_date',
            'commission_percentage', 'commission_value',
        ]

    # Hidden latitude and longitude fields
    latitude = forms.FloatField(required=False, widget=forms.HiddenInput())
    longitude = forms.FloatField(required=False, widget=forms.HiddenInput())

    # Checkbox fields
    has_parking = forms.BooleanField(required=False)
    furnished = forms.BooleanField(required=False)
    pool = forms.BooleanField(required=False)
    garden = forms.BooleanField(required=False)
    carports = forms.BooleanField(required=False)
    flatlet = forms.BooleanField(required=False)
    domestic_accommodation = forms.BooleanField(required=False)
    roof = forms.BooleanField(required=False)
    security = forms.BooleanField(required=False)
    study = forms.BooleanField(required=False)
    laundry = forms.BooleanField(required=False)
    patio = forms.BooleanField(required=False)
    balcony = forms.BooleanField(required=False)
    store_room = forms.BooleanField(required=False)
    views = forms.BooleanField(required=False)

    # Date fields
    occupation_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    mandate_start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    mandate_end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    # ---------------- Grouped fields for template ----------------
    basic_fields = [
        'title', 'description', 'province', 'location', 'listing_type',
        'property_type', 'price', 'area'
    ]

    property_specs_fields = [
        'number_of_bedrooms', 'number_of_kitchens', 'number_of_bathrooms',
        'number_of_garages', 'floor_area_m2', 'erf_size_m2',
        'price_per_m2', 'price_per_erf_m2', 'has_parking', 'number_of_parking_slots',
        'unit_no', 'complex_name', 'erf_no', 'ownership_type',
        'township', 'section_number', 'scheme_number', 'scheme_name'
    ]

    property_features_fields = [
        'study', 'lounges', 'dining_rooms', 'laundry', 'patio', 'balcony',
        'domestic_accommodation', 'carports', 'flatlet', 'store_room', 'furnished',
        'pool', 'security', 'roof', 'garden', 'views', 'walling', 'flooring'
    ]

    lease_fields = [
        'lease_period', 'occupation_date', 'deposit', 'lease_excludes', 'annual_escalation'
    ]

    mandate_fields = [
        'mandate_type', 'mandate_start_date', 'mandate_end_date',
        'commission_percentage', 'commission_value'
    ]


        
class SubmitPropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = [
            'title', 'description','province', 'location','listing_type', 'property_type', 'price',
            'number_of_bedrooms', 'number_of_kitchens', 'number_of_bathrooms',
            'number_of_garages', 'floor_area_m2', 'erf_size_m2',
            'price_per_m2', 'price_per_erf_m2', 'has_parking', 'number_of_parking_slots'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'latitude': forms.NumberInput(attrs={'step': 'any'}),
            'longitude': forms.NumberInput(attrs={'step': 'any'}),
        }

class InterestForm(forms.ModelForm):
    class Meta:
        model = Interest
        fields = ['interest_type', 'message', 'offer_price','contact_number']

        widgets = {
            'interest_type': forms.Select(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'offer_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

# This form is used for submitting a bid on an auction
# It includes a field for the bid amount and uses a NumberInput widget for better user experience
class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['amount']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your bid amount',
                'step': '0.01',
            }),
        }
        

# This form is used for creating a new agency
# It includes fields for the agency name, description, and owner.
class AgencyForm(forms.ModelForm):
    class Meta:
        model = Agency
        fields = ['name', 'address', 'description', 'contact_email', 'phone_number', 'logo']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control form-control-dark text-white bg-black bg-opacity-50 border border-secondary rounded',
                'placeholder': 'Enter agency name'
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control form-control-dark text-white bg-black bg-opacity-50 border border-secondary rounded',
                'placeholder': 'Enter address'
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control form-control-dark text-white bg-black bg-opacity-50 border border-secondary rounded',
                'placeholder': 'Enter description'
            }),
            'contact_email': forms.EmailInput(attrs={
                'class': 'form-control form-control-dark text-white bg-black bg-opacity-50 border border-secondary rounded',
                'placeholder': 'Enter contact email'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control form-control-dark text-white bg-black bg-opacity-50 border border-secondary rounded',
                'placeholder': 'Enter phone number'
            }),
            'logo': forms.ClearableFileInput(attrs={
                'class': 'form-control form-control-dark text-white bg-black bg-opacity-50 border border-secondary rounded'
            }),
        }


