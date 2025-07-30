from django import forms
from agencylistings.models import AgencyProperty
from django.contrib.auth import get_user_model

User = get_user_model()

class AgencyPropertyForm(forms.ModelForm):
    class Meta:
        model = AgencyProperty
        fields = [
            'title', 'description', 'province', 'location',
            'listing_type', 'property_type', 'price',
            'number_of_bedrooms', 'number_of_kitchens', 'number_of_bathrooms',
            'number_of_garages', 'floor_area_m2', 'erf_size_m2',
            'price_per_m2', 'price_per_erf_m2', 'has_parking', 'number_of_parking_slots',
            'agent'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'has_parking': forms.CheckboxInput(),
        }

    def __init__(self, *args, **kwargs):
        agency = kwargs.pop('agency', None)
        super().__init__(*args, **kwargs)

        if agency:
            self.fields['agent'].queryset = User.objects.filter(agentprofile__agency=agency)

        self.fields['agent'].required = False
        self.fields['agent'].label = "Assign Agent (optional)"
