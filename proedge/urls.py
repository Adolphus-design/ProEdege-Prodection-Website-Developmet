from django.urls import path
from .views import buyer_dashboard, edit_profile, register_view, CustomLoginView, CustomLogoutView, dashboard_redirect_view, seller_dashboard, tenant_dashboard, agent_dashboard, landlord_dashboard, bank_dashboard, auctioneer_dashboard, user_profile_view

# This file defines the URL patterns for the proedge app.
urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('dashboard/', dashboard_redirect_view, name='dashboard_redirect'),
    path('dashboard/buyer/', buyer_dashboard, name='buyer_dashboard'),
    path('dashboard/seller/', seller_dashboard, name='seller_dashboard'),
    path('dashboard/agent/', agent_dashboard, name='agent_dashboard'),
    path('dashboard/landlord/', landlord_dashboard, name='landlord_dashboard'),
    path('dashboard/tenant/', tenant_dashboard, name='tenant_dashboard'),
    path('dashboard/bank/', bank_dashboard, name='bank_dashboard'),
    path('dashboard/auctioneer/', auctioneer_dashboard, name='auctioneer_dashboard'),
    path('edit-profile/', edit_profile, name='edit_profile'),
    path('profile/', user_profile_view, name='user_profile'),
]
