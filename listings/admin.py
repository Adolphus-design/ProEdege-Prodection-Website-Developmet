from email.headerregistry import Group
from django.contrib import admin
from .models import Property
from .models import PropertyImage
from .models import Interest
from .models import Auction, Bid, Agency, AgentProfile

admin.site.register(Auction)
admin.site.register(Bid)
admin.site.register(Agency)
admin.site.register(AgentProfile)


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'price', 'status', 'created_at')
    list_filter = ('status', 'property_type', 'listing_type', 'created_at')
    search_fields = ('title', 'location', 'description')
    actions = ['approve_selected']

    def approve_selected(self, request, queryset):
        queryset.update(status='approved')
    approve_selected.short_description = "Mark selected properties as approved"

# Register the PropertyImage model with the admin site
admin.site.register(PropertyImage)


# Register the Interest model with the admin site
admin.site.register(Interest)