from django.contrib import admin
from .models import Property
from .models import PropertyImage

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'price', 'status', 'created_at')
    list_filter = ('status', 'property_type', 'listing_type', 'created_at')
    search_fields = ('title', 'location', 'description')
    actions = ['approve_selected']

    def approve_selected(self, request, queryset):
        queryset.update(status='approved')
    approve_selected.short_description = "Mark selected properties as approved"


admin.site.register(PropertyImage)