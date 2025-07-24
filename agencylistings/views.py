from django.shortcuts import render, get_object_or_404, redirect
from .forms import PropertyForm
from listings.forms import PropertyForm
from listings.models import Agency, Property
from django.contrib.auth.decorators import login_required


# Create your views here.
@login_required
def agency_property_list(request):
    properties = Property.objects.all()  # Later: filter by agency
    return render(request, 'agencylistings/agency_property_list.html', {'properties': properties})

# View: Property Detail
def agency_property_detail(request, pk):
    property = get_object_or_404(Property, pk=pk)
    return render(request, 'agencylistings/agency_property_detail.html', {'property': property})

# View: Edit Property
def edit_agency_property(request, pk):
    property = get_object_or_404(Property, pk=pk)

    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES, instance=property)
        if form.is_valid():
            form.save()
            return redirect('agency_property_list')
    else:
        form = PropertyForm(instance=property)

    return render(request, 'agencylistings/edit_agency_property.html', {'form': form, 'property': property})



# Add Property
@login_required
def add_agency_property(request):
    try:
        agency = Agency.objects.get(owner=request.user)
    except Agency.DoesNotExist:
        return redirect('agency_dashboard')  # Fallback if agency not found

    if request.method == 'POST':
        form = PropertyForm(request.POST)
        if form.is_valid():
            property = form.save(commit=False)
            property.agency = agency
            property.save()
            return redirect('agency_property_list')
    else:
        form = PropertyForm()

    return render(request, 'agencylisting/add_agency_property.html', {'form': form})