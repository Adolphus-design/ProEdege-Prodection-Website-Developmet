from django.db import models

from django.db import models
from django.conf import settings

class Property(models.Model):
    PROPERTY_TYPE_CHOICES = [
        ('house', 'House'),
        ('apartment', 'Apartment'),
        ('land', 'Vacant Land'),
        ('commercial', 'Commercial'),
        ('industrial', 'Industrial'),
    ]

    LISTING_TYPE_CHOICES = [
        ('private', 'Private Seller'),
        ('agent', 'Agent'),
        ('bank', 'Bank Property'),
    ]
    
    status = models.CharField(
    max_length=20,
    choices=[
        ('approved', 'Approved'),
        ('pending', 'Pending'),
        ('rejected', 'Rejected'),
        ('sold', 'Sold'),
    ],
    
)

    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    location = models.CharField(max_length=255)
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPE_CHOICES)
    listing_type = models.CharField(max_length=20, choices=LISTING_TYPE_CHOICES, default='private')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    floor_plan = models.FileField(upload_to='floor_plans/', null=True, blank=True)
    number_of_rooms = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, default='approved')
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='properties')
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='purchased_properties')
    landlord = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='rented_properties')
    tenant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='rented_by_properties')
    agent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='listed_properties')
    bank = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='banked_properties')
<<<<<<< HEAD
=======
    agency = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='agency_properties')
>>>>>>> f9ec739 (Before improving user deashboards and list, detail views to look modern)
    auctioneer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='auctioned_properties')
    created_at = models.DateTimeField(auto_now_add=True)
    
    #Additional fields for submit property form
    number_of_bedrooms = models.PositiveIntegerField(null=True, blank=True)
    number_of_kitchens = models.PositiveIntegerField(null=True, blank=True)
    number_of_bathrooms = models.PositiveIntegerField(null=True, blank=True)
    number_of_garages = models.PositiveIntegerField(null=True, blank=True)
    floor_area_m2 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    erf_size_m2 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_per_m2 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_per_erf_m2 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    has_parking = models.BooleanField(default=False)
    number_of_parking_slots = models.CharField(max_length=10, blank=True, default="N/A")

    def __str__(self):
        return f"{self.title} - {self.location} - R{self.price}"

    class Meta:
        verbose_name_plural = "Properties"


# listings/models.py
# This model represents images associated with a property listing.
# Each property can have multiple images, and this model establishes a foreign key relationship with the Property
class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='property_images/')
    main_image = models.ImageField(upload_to='property_main_images/', null=True, blank=True)


    def __str__(self):
        return f"Image for {self.property.title}"
