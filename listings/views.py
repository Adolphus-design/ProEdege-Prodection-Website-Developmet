from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Property, PropertyImage, Agency, AgentProfile
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .forms import SubmitPropertyForm
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from .forms import PropertyForm, PropertyImageForm
from django.contrib import messages
from .models import  Property, Interest, Agency
from django.http import HttpResponseForbidden
from .forms import InterestForm
from django.views.decorators.http import require_POST
from django.urls import reverse


# This view handles the listing of properties
# It retrieves all approved properties and paginates them for display
def property_list(request):
    query = request.GET.get('q')

    # Start with approved + sold
    properties = Property.objects.filter(Q(status='approved') | Q(status='sold'))

    if query:
        properties = properties.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(location__icontains=query) |
            Q(property_type__icontains=query) |
            Q(price__icontains=query) |
            Q(number_of_rooms__icontains=query)
        )

    context = {
        'properties': properties,
        'query': query
    }
    return render(request, 'listings/property_list.html', context)

# This view handles the detail view of a specific property
# It retrieves a property by its primary key (pk) and ensures it is approved
from django.shortcuts import get_object_or_404

# listings/views.py
from django.shortcuts import render, get_object_or_404
from .models import Property



def property_detail(request, pk):
    try:
        prop = Property.objects.get(pk=pk)
    except Property.DoesNotExist:
        return render(request, '404.html', status=404)

    user_role = getattr(request.user, 'role', None)
    allowed = False

    # Allow viewing if property is approved/sold
    if prop.status in ['approved', 'sold']:
        allowed = True
    else:
        # Check if the current user owns this property based on their role
        if user_role == 'seller' and prop.seller == request.user:
            allowed = True
        elif user_role == 'agency' and prop.agency == getattr(request.user, 'agency_profile', None):
            allowed = True
        elif user_role == 'agent' and prop.agent == request.user:
            allowed = True
        elif user_role == 'bank' and prop.bank == request.user:
            allowed = True
        elif user_role == 'auctioneer' and prop.auctioneer == request.user:
            allowed = True
        elif user_role == 'landlord' and prop.landlord == request.user:
            allowed = True
        elif user_role == 'tenant' and prop.tenant == request.user:
            allowed = True
        elif user_role == 'buyer' and prop.buyer == request.user:
            allowed = True

    if not allowed:
        return HttpResponseForbidden("You are not allowed to view this property.")

    # Determine the dashboard URL dynamically
    dashboard_url_name = 'dashboard_redirect'  # fallback
    role_dashboard_map = {
        'seller': 'seller_dashboard',
        'agent': 'agent_dashboard',
        'buyer': 'buyer_dashboard',
        'tenant': 'tenant_dashboard',
        'landlord': 'landlord_dashboard',
        'auctioneer': 'auctioneer_dashboard',
        'bank': 'bank_dashboard',
        'agency': 'agency_dashboard',
    }
    dashboard_url_name = role_dashboard_map.get(user_role, 'dashboard_redirect')

    images = prop.images.all()

    return render(request, 'listings/property_detail.html', {
        'property': prop,
        'images': images,
        'user_dashboard_url_name': dashboard_url_name,
    })

# This view allows sellers or agents to submit a new property listing
# It checks the user's role and renders a form for submitting property details

@login_required
def submit_property(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            property = form.save(commit=False)

            # Map user roles to Property fields
            role_field_map = {
                'seller': 'seller',
                'agent': 'agent',
                'agency': 'agency',
                'bank': 'bank',
                'landlord': 'landlord',
                'tenant': 'tenant',
                'auctioneer': 'auctioneer',
            }

            user_role = getattr(request.user, 'role', None)
            field_name = role_field_map.get(user_role)

            if field_name == 'agency':
                try:
                    setattr(property, 'agency', request.user.agency_profile)
                except Agency.DoesNotExist:
                    return redirect('create_agency_profile')
            elif field_name:
                setattr(property, field_name, request.user)

            property.status = 'approved'
            property.save()
            form.save_m2m()

            # 🔥 UNIVERSAL redirect: all roles go to upload images
            return redirect('upload_property_images', pk=property.pk)

    else:
        form = PropertyForm()

    return render(request, 'listings/submit_property.html', {'form': form})


# This view allows sellers or agents to edit an existing property listing
@login_required
def edit_property(request, pk):
    prop = get_object_or_404(Property, pk=pk, seller=request.user)  # only allow user to edit their own

    if request.method == 'POST':
        form = SubmitPropertyForm(request.POST, request.FILES, instance=prop)
        image_form = PropertyImageForm(request.POST, request.FILES)

        if form.is_valid() and image_form.is_valid():
            form.save()

            # handle new image uploads
            images = request.FILES.getlist('images')
            for image in images:
                PropertyImage.objects.create(property=prop, image=image)

            messages.success(request, "Property updated successfully.")
            return redirect('property_detail', pk=prop.pk)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SubmitPropertyForm(instance=prop)
        image_form = PropertyImageForm()
        
    
    return render(request, 'listings/edit_property.html', {
        'form': form,
        'image_form': image_form,
        'property': prop,
    })

# This view allows sellers or agents to mark a property as sold 
@login_required   
def mark_property_sold(request, pk):
    prop = get_object_or_404(Property, pk=pk)

    if prop.seller == request.user:
        prop.status = 'sold'
        prop.save()
        messages.success(request, 'Property marked as sold.')
    else:
        messages.error(request, 'You are not authorized to update this property.')

    # Redirect back to user's dashboard
    return redirect_user_dashboard(request)



@login_required
def mark_property_available(request, pk):
    prop = get_object_or_404(Property, pk=pk)

    if prop.seller == request.user:
        prop.status = 'approved'
        prop.save()
        messages.success(request, 'Property marked as available.')
    else:
        messages.error(request, 'You are not authorized to update this property.')

    # Redirect back to user's dashboard
    return redirect_user_dashboard(request)

def redirect_user_dashboard(request):
    user = request.user

    if user.groups.filter(name='Agents').exists():
        return redirect('agent_dashboard')
    elif user.groups.filter(name='Sellers').exists():
        return redirect('seller_dashboard')
    elif user.groups.filter(name='Buyers').exists():
        return redirect('buyer_dashboard')
    elif user.groups.filter(name='Tenants').exists():
        return redirect('tenant_dashboard')
    elif user.groups.filter(name='Landlords').exists():
        return redirect('landlord_dashboard')
    elif user.groups.filter(name='Auctioneers').exists():
        return redirect('auctioneer_dashboard')
    elif user.groups.filter(name='Bank').exists():
        return redirect('bank_dashboard')
    else:
        return redirect('dashboard_redirect')
    
# This view allows sellers or agents to upload images for a property listing
# It checks the user's role and ensures they are the owner of the property before allowing image uploads    
@login_required
def upload_property_images(request, pk):
    try:
        property = Property.objects.get(pk=pk)
    except Property.DoesNotExist:
        return redirect('dashboard_redirect')  # fallback if property not found

    # Ensure the logged-in user has permission to upload images
    user_role = request.user.role
    allowed = False

    if user_role == 'seller' and property.seller == request.user:
        allowed = True
    elif user_role == 'agency' and property.agency == getattr(request.user, 'agency_profile', None):
        allowed = True
    elif user_role == 'agent':
        agent_profile = getattr(request.user, 'agentprofile', None)
        if agent_profile and property.agent == agent_profile:
            allowed = True
    elif user_role == 'bank' and property.bank == request.user:
        allowed = True
    elif user_role == 'auctioneer' and property.auctioneer == request.user:
        allowed = True
    elif user_role == 'landlord' and property.landlord == request.user:
        allowed = True
    elif user_role == 'tenant' and property.tenant == request.user:
        allowed = True
    elif user_role == 'buyer' and property.buyer == request.user:
        allowed = True

    if not allowed:
        return redirect('dashboard_redirect')  # deny access if not owner

    if request.method == 'POST':
        images = request.FILES.getlist('images')
        for img in images:
            PropertyImage.objects.create(property=property, image=img)
        return redirect('property_detail', pk=property.pk)

    return render(request, 'listings/upload_property_images.html', {'property': property})

@login_required
def contact_seller(request, property_id):
    property_obj = get_object_or_404(Property, id=property_id)
    seller_email = property_obj.seller.email

    if request.method == 'POST':
        message = request.POST.get('message')
        subject = f"New Inquiry about: {property_obj.title}"
        from_email = request.user.email
        buyer_name = request.user.get_full_name() or request.user.username

        email_body = f"""
        Hello {property_obj.seller.username},

        You have received a new message about your listing:
        "{property_obj.title}"

        From: {buyer_name}
        Email: {from_email}

        Message:
        {message}
        """

        #send_mail(subject, email_body, from_email, [seller_email])
        messages.success(request, "Your message has been sent to the seller.")

    return redirect('property_detail', pk=property_id)


#view for displaying provinces and aeras

# This view allows users to submit their interest in a property
# It checks if the user is logged in and renders a form for submitting interest details
@login_required
def submit_interest(request, property_id):
    property_obj = get_object_or_404(Property, id=property_id)

    if request.method == 'POST':
        form = InterestForm(request.POST)
        if form.is_valid():
            interest = form.save(commit=False)
            interest.user = request.user
            interest.property = property_obj
            interest.save()
            messages.success(request, "Your interest/offer has been submitted.")
            return redirect('property_detail', pk=property_obj.pk)
    else:
        form = InterestForm()

    return render(request, 'listings/submit_interest.html', {
        'form': form,
        'property': property_obj
    })
    
    
# This view allows sellers or agents to delete a property image
# It checks if the user is logged in and is the owner of the property before allowing deletion
@login_required
@require_POST
def delete_property_image(request, image_id):
    image = get_object_or_404(PropertyImage, id=image_id, property__seller=request.user)
    image.delete()
    messages.success(request, "Image deleted successfully.")
    return redirect('edit_property', pk=image.property.pk)