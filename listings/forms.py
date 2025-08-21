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
            'title', 'description', 'province', 'location', 'latitude', 'longitude', 'listing_type', 'property_type', 'price',
            'number_of_bedrooms', 'number_of_kitchens', 'number_of_bathrooms',
            'number_of_garages', 'floor_area_m2', 'erf_size_m2',
            'price_per_m2', 'price_per_erf_m2', 'has_parking', 'number_of_parking_slots'
        ]

    latitude = forms.FloatField(required=False, widget=forms.HiddenInput())
    longitude = forms.FloatField(required=False, widget=forms.HiddenInput())


        
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
            'description': forms.Textarea(attrs={'rows': 3}),
        }


