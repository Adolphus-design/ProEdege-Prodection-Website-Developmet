from django import forms
from bankdashboard import models

class BankPropertyForm(forms.ModelForm):  # ✅ FIXED
    class Meta:
        model = models.BankProperty
        fields = [
            'title', 'description', 'location', 'province', 'price',
            'number_of_bedrooms', 'number_of_bathrooms', 'number_of_kitchens',
            'number_of_garages', 'erf_size_m2', 'floor_area_m2', 'is_published'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
            'price': forms.NumberInput(attrs={'step': '0.01'}),
        }

class BankListingForm(forms.ModelForm):
    class Meta:
        model = models.BankListing
        fields = ['date_repossessed', 'is_under_auction', 'auctioneer', 'auction_date', 'notes']
