from django.urls import path
from . import views


app_name = 'agencylistings'

urlpatterns = [
    path('properties/', views.agency_property_list, name='agency_property_list'),
    path('properties/add/', views.add_agency_property, name='add_agency_property'),
    path('properties/<int:pk>/', views.agency_property_detail, name='agency_property_detail'),
    path('properties/<int:pk>/edit/', views.edit_agency_property, name='edit_agency_property'),
]