from django.urls import path
from .views import buyer_dashboard, create_auction, edit_profile, register_view, CustomLoginView, CustomLogoutView, dashboard_redirect_view, seller_dashboard, tenant_dashboard, agent_dashboard, landlord_dashboard, bank_dashboard, auctioneer_dashboard, user_profile_view
from . import views 
# This file defines the URL patterns for the proedge app.
urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', views.custom_logout, name='logout'),
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
    path('messages/', views.interest_messages_view, name='interest_messages'),
    path('auctioneer/dashboard/', views.auctioneer_dashboard, name='auctioneer_dashboard'),
    path('auctioneer/create-auction/', create_auction, name='create_auction'),
    path('auction/<int:auction_id>/', views.auction_detail, name='auction_detail'),
    path('auctions/<int:auction_id>/edit/', views.edit_auction, name='edit_auction'),
    #path('auctions/<int:auction_id>/', views.auction_detail, name='auction_detail'),
    path('dashboard/agency/', views.agency_dashboard, name='agency_dashboard'),
    path('complete-agency-profile/', views.complete_agency_profile, name='complete_agency_profile'),
    path('request-join-agency/', views.request_join_agency, name='request_join_agency'),
    #path('agency/handle-request/<int:request_id>/', views.handle_join_request, name='handle_join_request'),
    path('reject-join-request/<int:request_id>/', views.reject_join_request, name='reject_join_request'),
    path('approve-join-request/<int:request_id>/', views.approve_join_request, name='approve_join_request'),
    path('agency/edit/', views.edit_agency_profile, name='edit_agency_profile'),
    path('agency/profile/', views.view_agency_profile, name='view_agency_profile'),
    path('agency/create/', views.complete_agency_profile, name='create_agency_profile'),
    #path('logout/', views.custom_logout, name='logout'),
    
    

]
