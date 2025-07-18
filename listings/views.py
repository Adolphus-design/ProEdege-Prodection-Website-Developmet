from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Property, PropertyImage
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .forms import SubmitPropertyForm
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from .forms import PropertyForm, PropertyImageForm
from django.contrib import messages

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

@login_required
def property_detail(request, pk):
    try:
        prop = Property.objects.get(pk=pk)
    except Property.DoesNotExist:
        return render(request, '404.html', status=404)

    # User can view the property if it's approved or they are the owner
    if prop.status in ['approved', 'sold'] or prop.seller == request.user:
        # Determine dashboard URL name based on group
        if request.user.groups.filter(name='Agents').exists():
            dashboard_url_name = 'agent_dashboard'
        elif request.user.groups.filter(name='Sellers').exists():
            dashboard_url_name = 'seller_dashboard'
        elif request.user.groups.filter(name='Buyers').exists():
            dashboard_url_name = 'buyer_dashboard'
        elif request.user.groups.filter(name='Tenants').exists():
            dashboard_url_name = 'tenant_dashboard'
        elif request.user.groups.filter(name='Landlords').exists():
            dashboard_url_name = 'landlord_dashboard'
        elif request.user.groups.filter(name='Auctioneers').exists():
            dashboard_url_name = 'auctioneer_dashboard'
        elif request.user.groups.filter(name='Bank').exists():
            dashboard_url_name = 'bank_dashboard'
        else:
            dashboard_url_name = 'dashboard_redirect'

        images = prop.images.all()

        return render(request, 'listings/property_detail.html', {
            'property': prop,
            'images': images,
            'user_dashboard_url_name': dashboard_url_name,
        })

    # If the user isn't allowed to view
    return HttpResponseForbidden("You are not allowed to view this property.")

# This view allows sellers or agents to submit a new property listing
# It checks the user's role and renders a form for submitting property details

@login_required
def submit_property(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            property = form.save(commit=False)
            property.seller = request.user
            property.status = 'pending'  # Ensure property is pending by default
            property.save()
            form.save_m2m()

            # ✅ New redirect to upload images
            return redirect('upload_property_images', pk=property.pk)

            # ⛔️ (Optional backup - kept for reference)
            """
            if request.user.groups.filter(name='Sellers').exists():
                return redirect('seller_dashboard')
            elif request.user.groups.filter(name='Agents').exists():
                return redirect('agent_dashboard')
            elif request.user.groups.filter(name='Landlords').exists():
                return redirect('landlord_dashboard')
            elif request.user.groups.filter(name='Auctioneers').exists():
                return redirect('auctioneer_dashboard')
            elif request.user.groups.filter(name='Bank').exists():
                return redirect('bank_dashboard')
            elif request.user.groups.filter(name='Buyers').exists():
                return redirect('buyer_dashboard')
            elif request.user.groups.filter(name='Tenants').exists():
                return redirect('tenant_dashboard')
            else:
                return redirect('dashboard_redirect')
            """
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
    property = get_object_or_404(Property, pk=pk)

    # ✅ Only allow the owner of the property to upload images
    if property.seller != request.user:
        return HttpResponseForbidden("You are not allowed to upload images for this property.")

    if request.method == 'POST':
        main_image = request.FILES.get('main_image')
        gallery_images = request.FILES.getlist('images')

        if main_image:
            property.main_image = main_image
            property.save()

        for image in gallery_images:
            PropertyImage.objects.create(property=property, image=image)

        messages.success(request, "Images uploaded successfully.")
        return redirect('property_detail', pk=property.pk)

    return render(request, 'listings/upload_property_images.html', {'property': property})

<<<<<<< HEAD
=======
#for comit
>>>>>>> f9ec739 (Before improving user deashboards and list, detail views to look modern)
