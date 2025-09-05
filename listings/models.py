from django.db import models
from django.conf import settings
from datetime import timedelta
from django.utils import timezone

from django.contrib.auth.models import User


from django.db import models
from django.conf import settings

class Property(models.Model):
    # Choices
    PROPERTY_TYPE_CHOICES = [
        ('house', 'House'),
        ('apartment', 'Apartment'),
        ('land', 'Vacant Land'),
        ('commercial', 'Commercial'),
        ('industrial', 'Industrial'),
        ('to let', 'To Let'),
        ('plot', 'Plot'),
        
    ]

    PROVINCE_CHOICES = [
        ('Eastern Cape', 'Eastern Cape'),
        ('Free State', 'Free State'),
        ('Gauteng', 'Gauteng'),
        ('KwaZulu-Natal', 'KwaZulu-Natal'),
        ('Limpopo', 'Limpopo'),
        ('Mpumalanga', 'Mpumalanga'),
        ('Northern Cape', 'Northern Cape'),
        ('North West', 'North West'),
        ('Western Cape', 'Western Cape'),
    ]

    LISTING_TYPE_CHOICES = [
        ('private', 'Private Seller'),
        ('agent', 'Agent'),
        ('bank', 'Bank Property'),
        ('auction', 'Auction'),
    ]

    STATUS_CHOICES = [
        ('approved', 'Approved'),
        ('pending', 'Pending'),
        ('rejected', 'Rejected'),
        ('sold', 'Sold'),
    ]

    # ---------------- Basic Details ----------------
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    location = models.CharField(max_length=255)
    province = models.CharField(max_length=100, choices=PROVINCE_CHOICES)
    area = models.CharField(max_length=100, null=True, blank=True)
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPE_CHOICES)
    listing_type = models.CharField(max_length=20, choices=LISTING_TYPE_CHOICES, default='agent')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    latitude = models.DecimalField(max_digits=100, decimal_places=50, null=True, blank=True)
    longitude = models.DecimalField(max_digits=100, decimal_places=50, null=True, blank=True)
    floor_plan = models.FileField(upload_to='floor_plans/', null=True, blank=True)

    # ---------------- Property Specs ----------------
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
    unit_no = models.CharField(max_length=50, null=True, blank=True)
    complex_name = models.CharField(max_length=255, null=True, blank=True)
    erf_no = models.CharField(max_length=50, null=True, blank=True)
    ownership_type = models.CharField(max_length=50, choices=[('freehold', 'Freehold'), ('sectional', 'Sectional Title')], null=True, blank=True)
    
    # Missing fields that caused previous errors
    township = models.CharField(max_length=255, null=True, blank=True)
    section_number = models.CharField(max_length=50, null=True, blank=True)
    scheme_number = models.CharField(max_length=50, null=True, blank=True)
    scheme_name = models.CharField(max_length=255, null=True, blank=True)

    # ---------------- Property Features ----------------
    study = models.BooleanField(default=False)
    lounges = models.PositiveIntegerField(null=True, blank=True)
    dining_rooms = models.PositiveIntegerField(null=True, blank=True)
    laundry = models.BooleanField(default=False)
    patio = models.BooleanField(default=False)
    balcony = models.BooleanField(default=False)
    domestic_accommodation = models.BooleanField(default=False)
    carports = models.BooleanField(default=False)
    flatlet = models.BooleanField(default=False)
    store_room = models.BooleanField(default=False)
    furnished = models.BooleanField(default=False)
    pool = models.BooleanField(default=False)
    security = models.BooleanField(default=False)
    roof = models.BooleanField(default=False)
    garden = models.BooleanField(default=False)
    views = models.BooleanField(default=False)
    walling = models.CharField(max_length=255, null=True, blank=True)
    flooring = models.CharField(max_length=255, null=True, blank=True)

    # ---------------- Lease / Rental Details ----------------
    lease_period = models.CharField(max_length=50, null=True, blank=True)
    occupation_date = models.DateField(null=True, blank=True)
    deposit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    lease_excludes = models.TextField(null=True, blank=True)
    annual_escalation = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Commercial-specific
    gross_rental = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="R/m²")
    net_rental = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="R/m²")
    operating_costs = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="R/m²")
    rates = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="R/m²")

    # Sectional-specific
    levy_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    floor_level = models.CharField(max_length=50, null=True, blank=True)

    # Freehold-specific
    zoning = models.CharField(max_length=100, null=True, blank=True)

    # Common to both (optional)
    rates_and_taxes = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    municipality = models.CharField(max_length=255, null=True, blank=True)

    # ---------------- Mandate / Commission Details ----------------
    mandate_type = models.CharField(max_length=50, null=True, blank=True)
    mandate_start_date = models.DateField(null=True, blank=True)
    mandate_end_date = models.DateField(null=True, blank=True)
    commission_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    commission_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    # ---------------- User associations ----------------
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='properties', null=True, blank=True)
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='purchased_properties')
    landlord = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='rented_properties')
    tenant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='rented_by_properties')
    agent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='listed_properties')
    agents = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='properties_assigned')
    bank = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='banked_properties')
    auctioneer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='auctioned_properties')
    agency = models.ForeignKey('Agency', on_delete=models.CASCADE, null=True, blank=True, related_name='properties')
    listed_by_agent = models.ForeignKey("AgentProfile", on_delete=models.SET_NULL, null=True, blank=True)
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
    responded = models.BooleanField(default=False)
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