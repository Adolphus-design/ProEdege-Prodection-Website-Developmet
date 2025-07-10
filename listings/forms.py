# listings/forms.py

from django import forms
from .models import Property

# This form is used for submitting property images
# It allows multiple file uploads and uses a ClearableFileInput widget for better user experience.
from django import forms

class PropertyImageForm(forms.Form):
    images = forms.FileField(
        required=False,
        label="Upload Property Images"
    )


# This form is used for submitting a new property listing
# It includes fields for title, description, price, location, property type, listing type, latitude, longitude, and floor plan.
class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = [
            'title', 'description', 'location', 'property_type', 'price',
            'number_of_bedrooms', 'number_of_kitchens', 'number_of_bathrooms',
            'number_of_garages', 'floor_area_m2', 'erf_size_m2',
            'price_per_m2', 'price_per_erf_m2', 'has_parking', 'number_of_parking_slots'
        ]
        
class SubmitPropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = [
            'title', 'description', 'location', 'property_type', 'price',
            'number_of_bedrooms', 'number_of_kitchens', 'number_of_bathrooms',
            'number_of_garages', 'floor_area_m2', 'erf_size_m2',
            'price_per_m2', 'price_per_erf_m2', 'has_parking', 'number_of_parking_slots'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'latitude': forms.NumberInput(attrs={'step': 'any'}),
            'longitude': forms.NumberInput(attrs={'step': 'any'}),
        }
