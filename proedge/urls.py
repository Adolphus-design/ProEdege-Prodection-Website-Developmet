from django.urls import path
<<<<<<< HEAD
from .views import buyer_dashboard, register_view, CustomLoginView, CustomLogoutView, dashboard_redirect_view, seller_dashboard, tenant_dashboard, agent_dashboard, landlord_dashboard, bank_dashboard, auctioneer_dashboard
=======
from .views import buyer_dashboard, register_view, CustomLoginView, CustomLogoutView, dashboard_redirect_view, seller_dashboard, tenant_dashboard, agent_dashboard, landlord_dashboard, bank_dashboard, auctioneer_dashboard, login_register_view
>>>>>>> f9ec739 (Before improving user deashboards and list, detail views to look modern)

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
<<<<<<< HEAD
=======
    path('accounts/', login_register_view, name='login_register'),

>>>>>>> f9ec739 (Before improving user deashboards and list, detail views to look modern)
    path('dashboard/auctioneer/', auctioneer_dashboard, name='auctioneer_dashboard'),
# Add more URL patterns for other roles as needed
# and so on...

]
