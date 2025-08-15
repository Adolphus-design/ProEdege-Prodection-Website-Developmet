from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from .models import UserProfile
from listings.models import Bid, Auction
from .models import AgentJoinRequest
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from .models import AgentDocument

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'role', 'password1', 'password2']

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'profile_picture',
            'contact_number',
            'ffc_number',
            'years_experience',
            'address',
            'ffc_certificate',
            'id_copy',
            'proof_of_address',
        ]
        widgets = {
            'contact_number': forms.TextInput(attrs={'placeholder': 'ex. 0791111111'}),
            'address': forms.TextInput(attrs={'placeholder': 'ex. Gauteng, Benoni'}),
            'ffc_number': forms.TextInput(attrs={'placeholder': 'ex. 2025/123456/07'}),
            'years_experience': forms.NumberInput(attrs={'placeholder': 'ex. 5'}),
        }

    def clean_profile_picture(self):
        picture = self.cleaned_data.get('profile_picture')
        if picture:
            max_size = 2 * 1024 * 1024  # 2MB limit
            if picture.size > max_size:
                raise forms.ValidationError("Profile picture size cannot exceed 2MB.")
        return picture
    
    def clean_ffc_certificate(self):
        ffc = self.cleaned_data.get('ffc_certificate')
        if ffc and ffc.size > 5 * 1024 * 1024:
            raise ValidationError("FFC certificate must be under 5MB.")
        return ffc

    def clean_id_copy(self):
        id_doc = self.cleaned_data.get('id_copy')
        if id_doc and id_doc.size > 5 * 1024 * 1024:
            raise ValidationError("ID copy must be under 5MB.")
        return id_doc

    def clean_proof_of_address(self):
        poa = self.cleaned_data.get('proof_of_address')
        if poa and poa.size > 5 * 1024 * 1024:
            raise ValidationError("Proof of address must be under 5MB.")
        return poa

        
        
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


class AgentDocumentForm(forms.ModelForm):
    class Meta:
        model = AgentDocument
        fields = ['document_type', 'document']
        widgets = {
            'document_type': forms.Select(attrs={'class': 'form-select'}),
            'document': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class EmailVerifiedAuthenticationForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not user.is_email_verified:
            raise ValidationError(
                "Your email address is not verified. Please check your email and click the verification link.",
                code='email_not_verified',
            )
        
