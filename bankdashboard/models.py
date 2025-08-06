from django.db import models
from django.conf import settings

class BankProperty(models.Model):
    bank = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bank_properties')
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200)
    province = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=12, decimal_places=2)

    number_of_bedrooms = models.PositiveIntegerField(null=True, blank=True)
    number_of_bathrooms = models.PositiveIntegerField(null=True, blank=True)
    number_of_kitchens = models.PositiveIntegerField(null=True, blank=True)
    number_of_garages = models.PositiveIntegerField(null=True, blank=True)

    erf_size_m2 = models.PositiveIntegerField(null=True, blank=True)
    floor_area_m2 = models.PositiveIntegerField(null=True, blank=True)

    listing_date = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=True)
    is_repossessed = models.BooleanField(default=False)
    is_auction = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} - {self.bank.username}"

class BankListing(models.Model):
    property = models.ForeignKey(BankProperty, on_delete=models.CASCADE, related_name='listings')
    date_repossessed = models.DateField(null=True, blank=True)
    is_under_auction = models.BooleanField(default=False)
    auctioneer = models.CharField(max_length=100, null=True, blank=True)
    auction_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Listing for {self.property.title} - Auction: {self.is_under_auction}"