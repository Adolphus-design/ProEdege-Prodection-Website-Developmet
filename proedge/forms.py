from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from .models import UserProfile
from listings.models import Bid, Auction
from .models import AgentJoinRequest

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'role', 'password1', 'password2']

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['address', 'contact_number', 'profile_picture']
        widgets = {
            'contact_number': forms.TextInput(attrs={'placeholder': 'Enter contact number'}),
        }
        
from django.core.exceptions import ValidationError

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'contact_number', 'address']

    def clean_profile_picture(self):
        picture = self.cleaned_data.get('profile_picture')
        if picture:
            if picture.size > 2 * 1024 * 1024:  # 2MB limit
                raise ValidationError("Profile picture size must be under 2MB.")
        return picture

class AuctionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # extract user if passed
        super().__init__(*args, **kwargs)

    class Meta:
        model = Auction
        fields = ['property', 'start_time', 'end_time', 'minimum_bid', 'bid_increment', 'is_active']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
        



class AgentJoinRequestForm(forms.ModelForm):
    class Meta:
        model = AgentJoinRequest
        fields = ['agency', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 3}),
        }

        
