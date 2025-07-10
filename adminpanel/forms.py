from django import forms
from django.forms import modelformset_factory
from listings.models import PropertyImage
from django.forms.widgets import ClearableFileInput

class MultiFileInput(ClearableFileInput):
    allow_multiple_selected = True

PropertyImageFormSet = modelformset_factory(
    PropertyImage,
    fields=('image',),
    extra=3,  # Number of empty forms shown for new images
    can_delete=True  # Allow deleting images
)



class PropertyImageForm(forms.Form):
    images = forms.FileField(
        label='Property Images',
        widget=MultiFileInput(attrs={'multiple': True}),
        required=True,
        help_text='Upload one or more images.'
    )

