from django.db import models
from django.conf import settings
from datetime import timedelta
from django.utils import timezone

from django.contrib.auth.models import User


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

    STATUS_CHOICES = [
        ('approved', 'Approved'),
        ('pending', 'Pending'),
        ('rejected', 'Rejected'),
        ('sold', 'Sold'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    location = models.CharField(max_length=255)
    province = models.CharField(max_length=100)  # Now a free-text field
    area = models.CharField(max_length=100, null=True, blank=True)

    

    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPE_CHOICES)
    listing_type = models.CharField(max_length=20, choices=LISTING_TYPE_CHOICES, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    floor_plan = models.FileField(upload_to='floor_plans/', null=True, blank=True)

    # Property specs
   
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

    # User associations
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='properties', null=True, blank=True)
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='purchased_properties')
    landlord = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='rented_properties')
    tenant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='rented_by_properties')
    #agent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='listed_properties')
    agents = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='properties_assigned')
    bank = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='banked_properties')
    auctioneer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='auctioned_properties')
    agency = models.ForeignKey('Agency', on_delete=models.CASCADE, null=True, blank=True, related_name='properties')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.location} - R{self.price}"

    class Meta:
        verbose_name_plural = "Properties"

    def get_main_image_url(self):
        main_img = self.images.filter(main_image__isnull=False).first()
        if main_img and main_img.main_image:
            return main_img.main_image.url
        first_img = self.images.first()
        if first_img and first_img.image:
            return first_img.image.url
        return None


class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='property_images/')
    main_image = models.ImageField(upload_to='property_main_images/', null=True, blank=True)

    def __str__(self):
        return f"Image for {self.property.title}"
    
# This model is used to store user interests in properties
# It allows users to express interest in buying, renting, or making an offer on a property
class Interest(models.Model):
    INTEREST_TYPE_CHOICES = [
        ('buy', 'Buying'),
        ('rent', 'Renting'),
        ('offer', 'Make Offer'),
        ('inquiry', 'General Inquiry'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    property = models.ForeignKey('Property', on_delete=models.CASCADE, related_name='interests')
    interest_type = models.CharField(max_length=20, choices=INTEREST_TYPE_CHOICES, default='inquiry')
    message = models.TextField(blank=True, null=True)
    offer_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    contact_number = models.CharField(max_length=10, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('accepted', 'Accepted'),
            ('declined', 'Declined')
        ],
        default='pending'
    )

    def __str__(self):
        return f"{self.user} - {self.property.title} - {self.interest_type}"
    
    
class Auction(models.Model):
    property = models.OneToOneField('Property', on_delete=models.CASCADE, related_name='auction')
    auctioneer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    minimum_bid = models.DecimalField(max_digits=12, decimal_places=2)
    bid_increment = models.DecimalField(max_digits=12, decimal_places=2, default=1000.00)
    
    is_active = models.BooleanField(default=False)
    is_closed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Auction for {self.property.title}"

    def has_started(self):
        return timezone.now() >= self.start_time

    def has_ended(self):
        return timezone.now() >= self.end_time

    def duration(self):
        return self.end_time - self.start_time
    
class Bid(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='bids')
    bidder = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-amount', '-timestamp']

    def __str__(self):
        return f"{self.bidder} - {self.amount} on {self.auction.property.title}"
    
# This model is used to store agency information
# An agency can have multiple agents, and each agent can be associated with an agency
class Agency(models.Model):
    name = models.CharField(max_length=255)
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='agency_profile')
    address = models.TextField(blank=True)
    description = models.TextField(blank=True)
    contact_email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    logo = models.ImageField(upload_to='agency_logos/', blank=True, null=True)

    def __str__(self):
        return self.name


# This model is used to store agent profiles
# Each agent can be associated with an agency, and they can have their own profile
class AgentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    agency = models.ForeignKey(Agency, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return self.user.username