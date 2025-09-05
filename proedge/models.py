from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from datetime import timedelta
from django.utils import timezone
from listings.models import Agency, AgentProfile
from django.core.validators import FileExtensionValidator
from django.utils import timezone
# Create your models here.

def user_profile_picture_path(instance, filename):
    return f"user_{instance.user.id}/profile_pictures/{filename}"


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255, blank=True)
    profile_picture = models.ImageField(upload_to=user_profile_picture_path, blank=True, null=True)
    contact_number = models.CharField(max_length=10, blank=False)
    address = models.CharField(max_length=255)
    is_profile_complete = models.BooleanField(default=False)

    agency = models.ForeignKey('listings.Agency', on_delete=models.SET_NULL, null=True, blank=True)

    ffc_number = models.CharField(max_length=64, blank=True)
    years_experience = models.PositiveIntegerField(default=0)

    # Agent verification documents
    ffc_certificate = models.FileField(upload_to='agent_docs/ffc_certificates/', blank=True, null=True)
    id_copy = models.FileField(upload_to='agent_docs/id_copies/', blank=True, null=True)
    proof_of_address = models.FileField(upload_to='agent_docs/proof_of_address/', blank=True, null=True)

    # Status fields for dynamic badges
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    ffc_certificate_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    id_copy_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    proof_of_address_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def check_document_status(self, document_field):
        """
        Checks a single document and returns 'pending', 'approved', or 'rejected'.
        """
        doc = getattr(self, document_field)
        if not doc:
            return 'pending'  # Document not uploaded
        if not doc.name.lower().endswith(('.pdf', '.jpg', '.jpeg', '.png')):
            return 'rejected'  # Invalid file type
        if doc.size > 5 * 1024 * 1024:
            return 'rejected'  # Exceeds 5MB
        return 'approved'  # Document exists and is valid

    def update_document_statuses(self):
        """
        Updates all document status fields based on current files.
        """
        self.ffc_certificate_status = self.check_document_status('ffc_certificate')
        self.id_copy_status = self.check_document_status('id_copy')
        self.proof_of_address_status = self.check_document_status('proof_of_address')
        self.save()

    def validate_documents(self):
        """
        Legacy method: Checks if all documents pass basic validation.
        """
        for file_field in [self.ffc_certificate, self.id_copy, self.proof_of_address]:
            if not file_field:
                return False
            if not file_field.name.lower().endswith(('.pdf', '.jpg', '.jpeg', '.png')):
                return False
            if file_field.size > 5 * 1024 * 1024:
                return False
        return True

    def __str__(self):
        return self.user.username
    
class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        #('buyer', 'Buyer'),
        #('seller', 'Seller'),
        #('tenant', 'Tenant'),
        #('agency', 'Agency'),
        #('landlord', 'Landlord'),
        ('agent', 'Agent'),
        #('bank', 'Bank'),
        #('auctioneer', 'Auctioneer'),
        
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='')
    email = models.EmailField(unique=True)
    is_email_verified = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.username} ({self.role})"


class Notification(models.Model):
    """
    Minimal notifications: one-way messages to any user.
    Later we can add categories, links, actions, etc.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=120)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    # Optional: point back to an object (e.g., join request)
    # content_type = models.ForeignKey(ContentType, null=True, blank=True, on_delete=models.SET_NULL)
    # object_id = models.PositiveIntegerField(null=True, blank=True)
    # generic = GenericForeignKey('content_type', 'object_id')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification(to={self.user}, title={self.title})"


# Agent Join Request
class AgentJoinRequest(models.Model):
    agent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE)
    message = models.TextField(blank=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    manual_rejection_reason = models.TextField(blank=True)

    # Keep auto check fields but do not use them for now
    auto_check_status = models.CharField(max_length=20, choices=[
        ('not_run','Not run'), 
        ('passed','Passed'), 
        ('failed','Failed')
    ], default='not_run')
    auto_check_notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.agent.username} → {self.agency.name}"
    

class AgentDocument(models.Model):
    DOC_TYPES = [
        ('ID', 'ID Copy'),
        ('FFC', 'FFC Certificate'),
    ]

    join_request = models.ForeignKey(AgentJoinRequest, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=10, choices=DOC_TYPES)
    document = models.FileField(upload_to='agent_docs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=10,
        choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')],
        default='pending'
    )
    rejection_reason = models.TextField(null=True, blank=True)
    automated_checked = models.BooleanField(default=False)
    expiry_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.join_request.agent.username} - {self.document_type} ({self.status})"


def practitioner_doc_upload_to(instance, filename):
    ts = timezone.now().strftime("%Y%m%d_%H%M%S")
    return f"practitioner_docs/user_{instance.user_id}/{instance.document_type}/{ts}_{filename}"


class PractitionerDocument(models.Model):
    """
    Generic per-user document store (does NOT replace AgentDocument; it's additive).
    We’ll use this for ongoing FFC/ID/etc. management on the profile.
    """

    DOC_TYPES = [
        ('ID', 'ID Copy'),
        ('FFC', 'FFC Certificate'),
        ('POA', 'Proof of Address'),
        ('QUAL', 'Qualification'),
        ('OTHER', 'Other'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='practitioner_documents',
    )
    document_type = models.CharField(max_length=20, choices=DOC_TYPES)
    file = models.FileField(
        upload_to=practitioner_doc_upload_to,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        help_text="PDF only."
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Auto-check fields (we'll wire the OCR/expiry logic later)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    automated_checked = models.BooleanField(default=False)
    rejection_reason = models.TextField(blank=True, null=True)

    # Dates parsed from the document (issue date → expiry, e.g. FFC=3y, ID stamp≈6mo)
    parsed_issue_date = models.DateField(blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)

    notes = models.TextField(blank=True)            # optional: store parse summary
    manual_override = models.BooleanField(default=False)  # when staff manually approves/rejects

    class Meta:
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['user', 'document_type']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.user} • {self.get_document_type_display()} • {self.status}"