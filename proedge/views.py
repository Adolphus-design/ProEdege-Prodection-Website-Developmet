from urllib import request
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm
from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.http import HttpResponse
from listings.models import Property
from django.db.models import Q
from collections import defaultdict


# This view handles user registration
# It uses the CustomUserCreationForm to create a new user account
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully! You can now log in.")
            return redirect('login')  # You’ll define this route later
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'proedge/register.html', {'form': form})

#code that haddles user login # logout and profile management will be added later
class CustomLoginView(LoginView):
    template_name = 'proedge/login.html'

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')
    
    
    #This view dasboard rediect depending on user role
@login_required
def dashboard_redirect_view(request):
    user = request.user
    if user.is_authenticated:
        role = getattr(user, 'role', None)  # Assuming 'role' is a field in your User model
        if role == 'seller':
            return redirect('seller_dashboard')
        elif role == 'buyer':
            return redirect('buyer_dashboard')
        elif role == 'agent':
            return redirect('agent_dashboard')
        elif role == 'landlord':
            return redirect('landlord_dashboard')
        elif role == 'tenant':
            return redirect('tenant_dashboard')
        # Add more roles as needed
        else:
            return redirect('property_list')  # or any safe default
    return redirect('login')

#This is the view for the buyer and seller dashboards
# You can create similar views for tenant, landlord, and agent dashboards
@login_required
def agent_dashboard(request):
    # Fetch properties related to the logged-in agent
    properties = Property.objects.filter(seller=request.user)

    context = {
        'properties': properties,
        'role': 'Agent',
    }

    return render(request, 'proedge/agent_dashboard.html', context)

@login_required
def seller_dashboard(request):
    query = request.GET.get('q')
    selected_status = request.GET.get('status')
    sort_by = request.GET.get('sort')

    # Unfiltered queryset for dashboard stats
    all_properties = Property.objects.filter(seller=request.user)

    # Filtered queryset for display
    properties = all_properties

    if selected_status in ['approved', 'rejected', 'pending', 'sold', 'available']:
        properties = properties.filter(status=selected_status)

    if query:
        properties = properties.filter(
            Q(title__icontains=query) |
            Q(location__icontains=query) |
            Q(description__icontains=query)
        )

    if sort_by == 'price_asc':
        properties = properties.order_by('price')
    elif sort_by == 'price_desc':
        properties = properties.order_by('-price')
    elif sort_by == 'newest':
        properties = properties.order_by('-created_at')
    elif sort_by == 'oldest':
        properties = properties.order_by('created_at')

    # ✅ Group properties by status for dynamic section display
    grouped_properties = defaultdict(list)
    for prop in properties:
        grouped_properties[prop.status].append(prop)

    context = {
        'grouped_properties': dict(grouped_properties),  # convert defaultdict to normal dict for template
        'role': 'Seller',
        'total_listings': all_properties.count(),
        'approved_count': all_properties.filter(status='approved').count(),
        'rejected_count': all_properties.filter(status='rejected').count(),
        'pending_count': all_properties.filter(status='pending').count(),
        'sold_count': all_properties.filter(status='sold').count(),
        'available_count': all_properties.filter(status='available').count(),
        'selected_status': selected_status,
        'query': query,
        'user_name': request.user.get_full_name() or request.user.username,
    }

    return render(request, 'proedge/seller_dashboard.html', context)

@login_required
def buyer_dashboard(request):
    query = request.GET.get('q')
    selected_status = request.GET.get('status')
    sort_by = request.GET.get('sort')

    # Unfiltered queryset for dashboard stats
    all_properties = Property.objects.filter(seller=request.user)

    # Filtered queryset for display
    properties = all_properties

    if selected_status in ['approved', 'rejected', 'pending', 'sold', 'available']:
        properties = properties.filter(status=selected_status)

    if query:
        properties = properties.filter(
            Q(title__icontains=query) |
            Q(location__icontains=query) |
            Q(description__icontains=query)
        )

    if sort_by == 'price_asc':
        properties = properties.order_by('price')
    elif sort_by == 'price_desc':
        properties = properties.order_by('-price')
    elif sort_by == 'newest':
        properties = properties.order_by('-created_at')
    elif sort_by == 'oldest':
        properties = properties.order_by('created_at')

    # ✅ Group properties by status for dynamic section display
    grouped_properties = defaultdict(list)
    for prop in properties:
        grouped_properties[prop.status].append(prop)

    context = {
        'grouped_properties': dict(grouped_properties),  # convert defaultdict to normal dict for template
        'role': 'Seller',
        'total_listings': all_properties.count(),
        'approved_count': all_properties.filter(status='approved').count(),
        'rejected_count': all_properties.filter(status='rejected').count(),
        'pending_count': all_properties.filter(status='pending').count(),
        'sold_count': all_properties.filter(status='sold').count(),
        'available_count': all_properties.filter(status='available').count(),
        'selected_status': selected_status,
        'query': query,
        'user_name': request.user.get_full_name() or request.user.username,
    }

    return render(request, 'proedge/buyer_dashboard.html', context)

@login_required
def landlord_dashboard(request):
    query = request.GET.get('q')
    selected_status = request.GET.get('status')
    sort_by = request.GET.get('sort')

    # Unfiltered queryset for dashboard stats
    all_properties = Property.objects.filter(seller=request.user)

    # Filtered queryset for display
    properties = all_properties

    if selected_status in ['approved', 'rejected', 'pending', 'sold', 'available']:
        properties = properties.filter(status=selected_status)

    if query:
        properties = properties.filter(
            Q(title__icontains=query) |
            Q(location__icontains=query) |
            Q(description__icontains=query)
        )

    if sort_by == 'price_asc':
        properties = properties.order_by('price')
    elif sort_by == 'price_desc':
        properties = properties.order_by('-price')
    elif sort_by == 'newest':
        properties = properties.order_by('-created_at')
    elif sort_by == 'oldest':
        properties = properties.order_by('created_at')

    # ✅ Group properties by status for dynamic section display
    grouped_properties = defaultdict(list)
    for prop in properties:
        grouped_properties[prop.status].append(prop)

    context = {
        'grouped_properties': dict(grouped_properties),  # convert defaultdict to normal dict for template
        'role': 'Seller',
        'total_listings': all_properties.count(),
        'approved_count': all_properties.filter(status='approved').count(),
        'rejected_count': all_properties.filter(status='rejected').count(),
        'pending_count': all_properties.filter(status='pending').count(),
        'sold_count': all_properties.filter(status='sold').count(),
        'available_count': all_properties.filter(status='available').count(),
        'selected_status': selected_status,
        'query': query,
        'user_name': request.user.get_full_name() or request.user.username,
    }

    return render(request, 'proedge/landlord_dashboard.html', context)

@login_required
def tenant_dashboard(request):
    query = request.GET.get('q')
    selected_status = request.GET.get('status')
    sort_by = request.GET.get('sort')

    # Unfiltered queryset for dashboard stats
    all_properties = Property.objects.filter(seller=request.user)

    # Filtered queryset for display
    properties = all_properties

    if selected_status in ['approved', 'rejected', 'pending', 'sold', 'available']:
        properties = properties.filter(status=selected_status)

    if query:
        properties = properties.filter(
            Q(title__icontains=query) |
            Q(location__icontains=query) |
            Q(description__icontains=query)
        )

    if sort_by == 'price_asc':
        properties = properties.order_by('price')
    elif sort_by == 'price_desc':
        properties = properties.order_by('-price')
    elif sort_by == 'newest':
        properties = properties.order_by('-created_at')
    elif sort_by == 'oldest':
        properties = properties.order_by('created_at')

    # ✅ Group properties by status for dynamic section display
    grouped_properties = defaultdict(list)
    for prop in properties:
        grouped_properties[prop.status].append(prop)

    context = {
        'grouped_properties': dict(grouped_properties),  # convert defaultdict to normal dict for template
        'role': 'Seller',
        'total_listings': all_properties.count(),
        'approved_count': all_properties.filter(status='approved').count(),
        'rejected_count': all_properties.filter(status='rejected').count(),
        'pending_count': all_properties.filter(status='pending').count(),
        'sold_count': all_properties.filter(status='sold').count(),
        'available_count': all_properties.filter(status='available').count(),
        'selected_status': selected_status,
        'query': query,
        'user_name': request.user.get_full_name() or request.user.username,
    }

    return render(request, 'proedge/tenant_dashboard.html', context)

@login_required
def bank_dashboard(request):
    query = request.GET.get('q')
    selected_status = request.GET.get('status')
    sort_by = request.GET.get('sort')

    # Unfiltered queryset for dashboard stats
    all_properties = Property.objects.filter(seller=request.user)

    # Filtered queryset for display
    properties = all_properties

    if selected_status in ['approved', 'rejected', 'pending', 'sold', 'available']:
        properties = properties.filter(status=selected_status)

    if query:
        properties = properties.filter(
            Q(title__icontains=query) |
            Q(location__icontains=query) |
            Q(description__icontains=query)
        )

    if sort_by == 'price_asc':
        properties = properties.order_by('price')
    elif sort_by == 'price_desc':
        properties = properties.order_by('-price')
    elif sort_by == 'newest':
        properties = properties.order_by('-created_at')
    elif sort_by == 'oldest':
        properties = properties.order_by('created_at')

    # ✅ Group properties by status for dynamic section display
    grouped_properties = defaultdict(list)
    for prop in properties:
        grouped_properties[prop.status].append(prop)

    context = {
        'grouped_properties': dict(grouped_properties),  # convert defaultdict to normal dict for template
        'role': 'Seller',
        'total_listings': all_properties.count(),
        'approved_count': all_properties.filter(status='approved').count(),
        'rejected_count': all_properties.filter(status='rejected').count(),
        'pending_count': all_properties.filter(status='pending').count(),
        'sold_count': all_properties.filter(status='sold').count(),
        'available_count': all_properties.filter(status='available').count(),
        'selected_status': selected_status,
        'query': query,
        'user_name': request.user.get_full_name() or request.user.username,
    }

    return render(request, 'proedge/bank_dashboard.html', context)

@login_required
def auctioneer_dashboard(request):
    properties = Property.objects.filter(seller=request.user)
    context = {
        'properties': properties,
        'role': 'Auctioneer',
    }
    return render(request, 'proedge/auctioneer_dashboard.html', context)

# Add similar ones for tenant, landlord, agent
