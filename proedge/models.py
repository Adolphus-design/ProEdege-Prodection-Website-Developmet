from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
# Create your models here.

def user_profile_picture_path(instance, filename):
    return f'profile_pictures/user_{instance.user.id}/{filename}'

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255, blank=True)
    profile_picture = models.ImageField(upload_to=user_profile_picture_path, blank=True, null=True)
    contact_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    is_profile_complete = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
    
class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
        ('tenant', 'Tenant'),
        ('landlord', 'Landlord'),
        ('agent', 'Agent'),
        ('bank', 'Bank'),
        ('auctioneer', 'Auctioneer'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    
    def __str__(self):
        return f"{self.username} ({self.role})"
