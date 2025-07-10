from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import get_user_model
from listings.models import Property
from django.db.models import Q  
from django import forms
from django.contrib import messages
from listings.models import Property, PropertyImage
from .forms import PropertyImageFormSet, PropertyImageForm
from django.contrib.admin.views.decorators import staff_member_required

User = get_user_model()

def staff_required(view_func):
    return user_passes_test(lambda u: u.is_staff)(view_func)

@staff_required
def dashboard(request):
    user_count = User.objects.count()
    property_count = Property.objects.count()
    pending_properties = Property.objects.filter(status='pending').count()

    context = {
        'user_count': user_count,
        'property_count': property_count,
        'pending_properties': pending_properties,
    }
    return render(request, 'adminpanel/dashboard.html', context)

@staff_required
def user_list(request):
    users = User.objects.all()
    return render(request, 'adminpanel/user_list.html', {'users': users})

@staff_required
def edit_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    # Implement user edit form (assign roles, toggle staff, active)
    # For now, simple example:
    if request.method == 'POST':
        is_staff = 'is_staff' in request.POST
        is_active = 'is_active' in request.POST
        user.is_staff = is_staff
        user.is_active = is_active
        user.save()
        return redirect('adminpanel:user_list')

    return render(request, 'adminpanel/edit_user.html', {'user': user})

@staff_required


@staff_required
def property_list(request):
    query = request.GET.get('q')

    # Apply search filters to all property statuses
    approved_properties = Property.objects.filter(status='approved')
    pending_properties = Property.objects.filter(status='pending')
    rejected_properties = Property.objects.filter(status='rejected')
    


    if query:
        approved_properties = approved_properties.filter(
            Q(title__icontains=query) | Q(location__icontains=query)
        )
        pending_properties = pending_properties.filter(
            Q(title__icontains=query) | Q(location__icontains=query)
        )
        rejected_properties = rejected_properties.filter(
            Q(title__icontains=query) | Q(location__icontains=query)
        )

    no_results = (
    not approved_properties.exists() and
    not pending_properties.exists() and
    not rejected_properties.exists()
)

    context = {
    'approved_properties': approved_properties,
    'pending_properties': pending_properties,
    'rejected_properties': rejected_properties,
    'query': query,
    'no_results': no_results,
}
    return render(request, 'adminpanel/property_list.html', context)


# This view allows staff to approve a property listing
@staff_required
def approve_property(request, pk):
    prop = get_object_or_404(Property, pk=pk)
    prop.status = 'approved'
    prop.save()
    return redirect('adminpanel:property_list')

# This view allows staff to reject a property listing
@staff_required
def reject_property(request, pk):
    prop = get_object_or_404(Property, pk=pk)
    prop.status = 'rejected'
    prop.save()
    return redirect('adminpanel:property_list')

# This view allows staff to delete a property listing
@staff_required
def delete_property(request, pk):
    prop = get_object_or_404(Property, pk=pk)
    prop.delete()
    return redirect('adminpanel:property_list')

# This view allows staff to view the details of a specific property
@staff_member_required
def property_detail(request, pk):
    prop = get_object_or_404(Property, pk=pk)

    if request.method == 'POST':
        form = PropertyImageForm(request.POST, request.FILES)
        files = request.FILES.getlist('images')  # use the field name from the form

        if form.is_valid():
            for f in files:
                PropertyImage.objects.create(property=prop, image=f)
            messages.success(request, "Images uploaded successfully.")
            return redirect('adminpanel:property_detail', pk=pk)
        else:
            messages.error(request, "Failed to upload images.")
    else:
        form = PropertyImageForm()

    context = {
        'property': prop,
        'form': form,
        'images': prop.images.all(),  # so you can show existing images if needed
    }
    return render(request, 'adminpanel/property_detail.html', context)




class AdminEditPropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = ['title', 'description', 'price', 'location', 'property_type', 'listing_type', 'latitude', 'longitude', 'status']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'latitude': forms.NumberInput(attrs={'step': 'any'}),
            'longitude': forms.NumberInput(attrs={'step': 'any'}),
        }
# This form is used for editing property details in the admin panel
# It includes fields for title, description, price, location, property type, listing type,
@staff_required
def edit_property(request, pk):
    prop = get_object_or_404(Property, pk=pk)
    
    if request.method == 'POST':
        form = AdminEditPropertyForm(request.POST, instance=prop)
        if form.is_valid():
            form.save()
            return redirect('adminpanel:property_detail', pk=prop.pk)
    else:
        form = AdminEditPropertyForm(instance=prop)
    
    return render(request, 'adminpanel/edit_property.html', {'form': form, 'property': prop})

def staff_required(view_func):
    return user_passes_test(lambda u: u.is_staff)(view_func)

# This view allows staff to edit property images    
@staff_required
def edit_property_images(request, pk):
    property_obj = get_object_or_404(Property, pk=pk)
    if request.method == 'POST':
        formset = PropertyImageFormSet(request.POST, request.FILES, queryset=PropertyImage.objects.filter(property=property_obj))
        if formset.is_valid():
            # Set the property for new images before saving
            instances = formset.save(commit=False)
            for instance in instances:
                instance.property = property_obj
                instance.save()
            # Delete images marked for deletion
            for obj in formset.deleted_objects:
                obj.delete()
            return redirect('adminpanel:property_list')
    else:
        formset = PropertyImageFormSet(queryset=PropertyImage.objects.filter(property=property_obj))

    context = {
        'property': property_obj,
        'formset': formset,
    }
    return render(request, 'adminpanel/edit_property_images.html', context)