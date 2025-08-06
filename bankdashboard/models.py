from django.db import models
from django.conf import settings
from listings.models import Property  # Assuming you use this globally

class BankListing(models.Model):
    bank = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bank_listings')
    property = models.OneToOneField(Property, on_delete=models.CASCADE)
    date_repossessed = models.DateField()
    is_under_auction = models.BooleanField(default=False)
    auctioneer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='assigned_auctions'
    )
    auction_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.property.title} - Repossessed by {self.bank.username}"
