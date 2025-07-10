from django.urls import path
from .views import property_list, edit_property, mark_property_sold
from . import views

urlpatterns = [
    #path('properties/', property_list, name='property_list'),
    #path('properties/<int:pk>/', property_detail, name='property_detail'),
    path('', views.property_list, name='property_list'),
    path('<int:pk>/', views.property_detail, name='property_detail'),
    path('submit/', views.submit_property, name='submit_property'),
    path('properties/<int:pk>/edit/', edit_property, name='edit_property'),
    path('properties/<int:pk>/mark-sold/', mark_property_sold, name='mark_property_sold'),
    path('properties/<int:pk>/mark-available/', views.mark_property_available, name='mark_property_available'),
    
    path('properties/<int:pk>/upload-images/', views.upload_property_images, name='upload_property_images'),

]
