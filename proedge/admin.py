from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, PractitionerDocument

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'role', 'is_staff', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('Role Info', {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role Info', {'fields': ('role',)}),
    )



@admin.register(PractitionerDocument)
class PractitionerDocumentAdmin(admin.ModelAdmin):
    list_display = ('user', 'document_type', 'status', 'uploaded_at', 'expiry_date', 'automated_checked')
    list_filter = ('document_type', 'status', 'automated_checked')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name')


admin.site.register(CustomUser, CustomUserAdmin)


