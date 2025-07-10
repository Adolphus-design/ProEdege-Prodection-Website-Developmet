from django.urls import path
from . import views

app_name = 'adminpanel'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('users/', views.user_list, name='user_list'),
    path('users/<int:user_id>/edit/', views.edit_user, name='edit_user'),
    path('properties/', views.property_list, name='property_list'),
    path('properties/<int:pk>/approve/', views.approve_property, name='approve_property'),
    path('properties/<int:pk>/reject/', views.reject_property, name='reject_property'),
    path('properties/<int:pk>/delete/', views.delete_property, name='delete_property'),
    path('properties/<int:pk>/', views.property_detail, name='property_detail'),
    path('properties/<int:pk>/edit/', views.edit_property, name='edit_property'),
    path('properties/<int:pk>/images/', views.edit_property_images, name='edit_property_images'),
    path('properties/<int:pk>/', views.property_detail, name='property_detail'),





]
