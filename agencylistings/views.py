from django.shortcuts import render, get_object_or_404, redirect

from listings.forms import PropertyForm
from listings.models import Agency, Property, AgentProfile
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .forms import AgencyPropertyForm



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
    if request.method == 'POST':
        form = AgencyPropertyForm(request.POST, request.FILES)
        if form.is_valid():
            agency_property = form.save(commit=False)
            agency_property.agency = request.user.agency_profile  # Or however you link
            agency_property.save()
            return redirect('agency_dashboard')  # or appropriate view
    else:
        form = AgencyPropertyForm()
    return render(request, 'agencylistings/add_agency_property.html', {'form': form})



# View: Submit Property
@login_required
def submit_agency_property(request):
    if request.method == 'POST':
        form = AgencyPropertyForm(request.POST, agency=request.user.agency_profile.agency)
        if form.is_valid():
            property = form.save(commit=False)
            property.agency = request.user.agency_profile.agency
            property.save()
            return redirect('agencylistings:agency_property_list')
    else:
        form = AgencyPropertyForm(agency=request.user.agency_profile.agency)

    return render(request, 'agencylistings/add_agency_property.html', {'form': form})