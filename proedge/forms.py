from django import forms
from django.contrib.auth.forms import UserCreationForm

from core import settings
from .models import CustomUser
from .models import UserProfile
from listings.models import Bid, Auction, Property
from .models import AgentJoinRequest
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from .models import AgentDocument

from django.contrib.auth import get_user_model

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

        



class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['ffc_certificate', 'id_copy', 'proof_of_address']

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

    def save(self, commit=True):
        profile = super().save(commit=False)

        # Reset status when new docs are uploaded
        if self.cleaned_data.get('ffc_certificate'):
            profile.ffc_certificate_status = 'pending'
        if self.cleaned_data.get('id_copy'):
            profile.id_copy_status = 'pending'
        if self.cleaned_data.get('proof_of_address'):
            profile.proof_of_address_status = 'pending'

        if commit:
            profile.save()
        return profile
    

        
        
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
        

User = get_user_model()

class AssignAgentForm(forms.Form):
    agent = forms.ModelChoiceField(
        queryset=UserProfile.objects.none(),  # We’ll set the queryset in the view
        label="Select Agent",
        widget=forms.Select(attrs={'class': 'form-select'})
    )


CustomUser = get_user_model()

class AgencyCreateAgentForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=False)  # optional on edit
    ffc_certificate = forms.FileField(required=False)
    id_copy = forms.FileField(required=False)
    proof_of_address = forms.FileField(required=False)
    profile_picture = forms.ImageField(required=False)  # ✅ Added profile picture

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'role']

    def save(self, commit=True, agency=None):
        user = super().save(commit=False)

        # Only set password if provided (edit mode)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)

        user.role = 'agent'
        user.is_active = True
        user.is_email_verified = True
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        if commit:
            user.save()

            # Update or create UserProfile to avoid UNIQUE constraint error
            profile, created = UserProfile.objects.get_or_create(user=user)

            if self.cleaned_data.get('ffc_certificate'):
                profile.ffc_certificate = self.cleaned_data['ffc_certificate']
            if self.cleaned_data.get('id_copy'):
                profile.id_copy = self.cleaned_data['id_copy']
            if self.cleaned_data.get('proof_of_address'):
                profile.proof_of_address = self.cleaned_data['proof_of_address']
            if self.cleaned_data.get('profile_picture'):  # ✅ Save profile picture
                profile.profile_picture = self.cleaned_data['profile_picture']

            if agency:
                profile.agency = agency
            profile.save()

        return user
