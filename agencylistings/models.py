# agencylistings/models.py
from django.db import models
from core import settings
from proedge.models import Agency
from django.utils import timezone
from django.conf import settings

class AgencyProperty(models.Model):
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, related_name='agency_properties')
    agent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    number_of_kitchens = models.PositiveIntegerField(default=0)
    number_of_bedrooms = models.PositiveIntegerField(default=0)
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    province = models.CharField(max_length=100)
    property_type = models.CharField(max_length=100, choices=[
        ('house', 'House'),
        ('apartment', 'Apartment'),
        ('commercial', 'Commercial'),
        ('vacant_land', 'Vacant Land'),
    ])
    listing_type = models.CharField(max_length=100, choices=[
        ('for_sale', 'For Sale'),
        ('to_rent', 'To Rent'),
        ('auction', 'Auction'),
    ])
    price = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)

    # Optional fields for detail
    
    number_of_bathrooms = models.PositiveIntegerField(null=True, blank=True)
    number_of_parking_slots = models.PositiveIntegerField(default=0)
    number_of_garages = models.PositiveIntegerField(null=True, blank=True)
    floor_area_m2 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    erf_size_m2 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    has_parking = models.BooleanField(default=False)
    number_of_parking_slots = models.PositiveIntegerField(null=True, blank=True)
    price_per_m2 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_per_erf_m2 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    def __str__(self):
        return f"{self.title} - {self.agency.name}"

    class Meta:
        ordering = ['-created_at']
