from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.


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
