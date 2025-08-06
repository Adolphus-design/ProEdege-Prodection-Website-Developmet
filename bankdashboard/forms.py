from django import forms
from .models import BankListing
from listings.models import Property

class BankPropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = [
            'title', 'description', 'price', 'number_of_bedrooms', 'number_of_bathro'
            'oms',
            'number_of_garages', 'number_of_kitchens', 'erf_size_m2', 'floor_area_m2',
            'location', 'property_type', 'listing_type'
        ]

class BankListingForm(forms.ModelForm):
    class Meta:
        model = BankListing
        fields = ['date_repossessed', 'is_under_auction', 'auctioneer', 'auction_date', 'notes']
