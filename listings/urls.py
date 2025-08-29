from django.urls import path
from .views import property_list, edit_property, mark_property_sold
from . import views
from .views import submit_interest



urlpatterns = [
    path('properties/', property_list, name='property_list'),
    #path('properties/<int:pk>/', property_detail, name='property_detail'),
    path('', views.property_list, name='property_list'),
    path('<int:pk>/', views.property_detail, name='property_detail'),
    path('submit/', views.submit_property, name='submit_property'),
    path('properties/<int:pk>/edit/', edit_property, name='edit_property'),
    path('properties/<int:pk>/mark-sold/', mark_property_sold, name='mark_property_sold'),
    path('properties/<int:pk>/mark-available/', views.mark_property_available, name='mark_property_available'),
    path('contact-seller/<int:property_id>/', views.contact_seller, name='contact_seller'),
    path('property/<int:pk>/upload-images/', views.upload_property_images, name='upload_property_images'),
    #path('landing/', views.landing_page, name='landing_page'),
    #path('province/<int:province_id>/', views.province_properties, name='province_properties'),
    path('property/<int:property_id>/interest/', views.submit_interest, name='submit_interest'),
    path('property/image/delete/<int:image_id>/', views.delete_property_image, name='delete_property_image'),
    path('properties/province/<str:province>/', views.province_properties, name='province_properties')

]
