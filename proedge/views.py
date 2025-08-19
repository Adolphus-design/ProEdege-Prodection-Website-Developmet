from email.message import Message
from urllib import request
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from proedge.utils import notify
from proedge.verification import automated_verify_agent_document
from proedge.email import notify_agency_new_join_request, notify_agent_request_decision
from .forms import CustomUserCreationForm
from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from .forms import DocumentUploadForm
from django.http import HttpResponse
from listings.models import Property
from django.db.models import Q
from collections import defaultdict
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from .forms import EditProfileForm
from .models import AgentDocument, CustomUser, UserProfile
from listings.models import Property, Interest, Agency
from collections import defaultdict
from .forms import AuctionForm
from django.contrib.auth import logout
from django.contrib.auth.decorators import user_passes_test
from listings.models import Property, Auction, Bid, Agency, AgentProfile
from listings.forms import BidForm, AgencyForm
from agencylistings.models import AgencyProperty
from .forms import AgentJoinRequestForm
from .models import AgentJoinRequest
from .forms import AgentDocumentForm, AgencyCreateAgentForm
from bankdashboard.forms import BankPropertyForm
from bankdashboard.models import BankProperty
from bankdashboard.forms import BankListingForm
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from .forms import EmailVerifiedAuthenticationForm, AgentDocument
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.forms import modelformset_factory
from django.contrib.auth import get_user_model
from django.contrib import messages
import fitz  # PyMuPDF
from django.core.paginator import Paginator
from .forms import AssignAgentForm
import re
from datetime import datetime
from .verification import automated_verify_agent_document




@login_required
def agency_agent_detail(request, pk):
    agent = get_object_or_404(CustomUser, pk=pk, role='agent')
    profile = get_object_or_404(UserProfile, user=agent)

    # Only allow the agency owner to view
    if request.user.agency_profile != profile.agency:
        return redirect('agency_dashboard')

    if request.method == "POST":
        form = AgencyCreateAgentForm(request.POST, request.FILES, instance=agent)
        if form.is_valid():
            form.save(agency=request.user.agency_profile)
            messages.success(request, "Agent profile updated successfully!")
            return redirect('agency_agent_detail', pk=agent.pk)
    else:
        form = AgencyCreateAgentForm(instance=agent)

    return render(request, 'proedge/agency_agent_detail.html', {
        'agent': agent,
        'profile': profile,
        'form': form,
    })



@login_required
def view_agents(request):
    try:
        agency = request.user.agency_profile
    except Agency.DoesNotExist:
        return redirect('create_agency_profile')
    
    agents = UserProfile.objects.filter(user__role='agent', agency=agency)
    
    return render(request, 'proedge/view_agents.html', {'agents': agents})

@login_required
def create_agent(request):
    try:
        agency = request.user.agency_profile
    except Agency.DoesNotExist:
        return redirect('create_agency_profile')
    
    if request.method == 'POST':
        form = AgencyCreateAgentForm(request.POST)
        if form.is_valid():
            agent = form.save(agency=agency)
            messages.success(request, f"Agent {agent.username} created successfully!")
            return redirect('agency_dashboard')
    else:
        form = AgencyCreateAgentForm()
    
    return render(request, 'proedge/create_agent.html', {'form': form})


@login_required
def create_agent(request):
    try:
        agency = request.user.agency_profile
    except Agency.DoesNotExist:
        return redirect('create_agency_profile')
    
    if request.method == 'POST':
        form = AgencyCreateAgentForm(request.POST, request.FILES)  # ✅ include FILES for docs
        if form.is_valid():
            agent = form.save(agency=agency)

            # ✅ Optional: Send welcome email
            send_mail(
                subject="Welcome to ProEdge Property Group",
                message=f"Hi {agent.username},\n\nYour agent account has been created and activated by {agency.name}. You can now log in using your credentials.\n\n- ProEdge Team",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[agent.email],
                fail_silently=True,
            )

            messages.success(request, f"Agent {agent.username} created and activated successfully!")
            return redirect('agency_dashboard')
    else:
        form = AgencyCreateAgentForm()
    
    return render(request, 'proedge/create_agent.html', {'form': form})


@login_required
def assign_agent_to_property(request, pk):
    property = get_object_or_404(Property, pk=pk)

    # Only agency owner can assign agents
    if not hasattr(request.user, 'agency_profile') or property.agency != request.user.agency_profile:
        messages.error(request, "You are not allowed to assign agents to this property.")
        return redirect('agency_dashboard')

    # Fetch all users with role='agent' under this agency
    agents = CustomUser.objects.filter(
        role='agent',
        userprofile__agency=request.user.agency_profile
    )

    if request.method == "POST":
        selected_agent_ids = request.POST.getlist('agents')
        # Convert to integers
        selected_agent_ids = [int(a) for a in selected_agent_ids if a.isdigit()]

        # Assign only existing users
        valid_agents = agents.filter(id__in=selected_agent_ids)
        property.agents.set(valid_agents)  # Use ManyToManyField
        property.save()

        messages.success(request, "Agent(s) assigned successfully.")
        return redirect('agency_dashboard')

    return render(request, 'proedge/assign_agent.html', {
        'property': property,
        'agents': agents
    })



@login_required
def upload_documents(request):
    user_profile = request.user.userprofile

    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()  # Save uploaded files
            user_profile.update_document_statuses()  # Auto-check and update status fields
            return redirect('user_profile')  # Redirect back to the profile view page
    else:
        form = DocumentUploadForm(instance=user_profile)

    context = {
        'form': form,
        'profile': user_profile  # pass profile to template for dynamic badges
    }
    return render(request, 'proedge/upload_documents.html', context)



# This view handles user registration
# It uses the CustomUserCreationForm to create a new user account
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # deactivate account until email confirmed
            user.save()

            current_site = get_current_site(request)
            subject = 'Activate your ProEdge account'
            
            html_message = render_to_string('proedge/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            plain_message = strip_tags(html_message)  # converts HTML to plain text
            
            email = EmailMultiAlternatives(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
            )
            email.attach_alternative(html_message, "text/html")
            email.send(fail_silently=False)

            messages.success(request, "Account created! Please check your email to activate your account.")
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'proedge/register.html', {'form': form})

def activate_account(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.is_email_verified = True    # <-- Add this line
        user.save()
        messages.success(request, "Your account has been activated. You can now log in.")
        return redirect('login')
    else:
        messages.error(request, "Activation link is invalid or expired.")
        return redirect('register')
    


#code that haddles user login # logout and profile management will be added later
class CustomLoginView(LoginView):
    template_name = 'proedge/login.html'
    authentication_form = EmailVerifiedAuthenticationForm

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')
    
    
    #This view dasboard rediect depending on user role
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

@login_required
def dashboard_redirect_view(request):
    user = request.user

    if user.is_authenticated:
        # First check if superuser, redirect to adminpanel dashboard
        if user.is_superuser:
            return redirect('adminpanel:dashboard')  # <-- use the URL name for your adminpanel dashboard view

        role = getattr(user, 'role', None)

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
        elif role == 'bank':
            return redirect('bank_dashboard')
        elif role == 'auctioneer':
            return redirect('auctioneer_dashboard')
        elif role == 'agency':
            if not hasattr(user, 'agency_profile'):
                return redirect('complete_agency_profile')
            return redirect('agency_dashboard')
        else:
            return redirect('property_list')

    return redirect('login')


#This is the view for the buyer and seller dashboards
# You can create similar views for tenant, landlord, and agent dashboards

@login_required
def agent_dashboard(request):
    user = request.user

    # ✅ Properties listed by the agent themselves
    self_listed_properties = Property.objects.filter(agent=user)

    # ✅ Properties assigned to this agent by the agency
    assigned_properties = Property.objects.filter(agents=user)

    # ✅ Combine QuerySets using union
    properties = (self_listed_properties | assigned_properties).distinct().order_by('-created_at')

    # Filtering logic
    query = request.GET.get('q')
    selected_status = request.GET.get('status')
    sort = request.GET.get('sort')

    if query:
        properties = properties.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(location__icontains=query)
        )

    if selected_status:
        properties = properties.filter(status=selected_status)

    if sort == 'price_asc':
        properties = properties.order_by('price')
    elif sort == 'price_desc':
        properties = properties.order_by('-price')
    elif sort == 'newest':
        properties = properties.order_by('-created_at')
    elif sort == 'oldest':
        properties = properties.order_by('created_at')

    # Group properties by status
    grouped_properties = defaultdict(list)
    for prop in properties:
        grouped_properties[prop.status].append(prop)

    # Interest/offers for this agent’s properties
    interests = Interest.objects.filter(property__in=properties).select_related('user', 'property')

    context = {
        'role': 'Agent',
        'properties': properties,
        'grouped_properties': dict(grouped_properties),
        'interests': interests,

        # Summary stats
        'total_listings': properties.count(),
        'approved_count': properties.filter(status='approved').count(),
        'pending_count': properties.filter(status='pending').count(),
        'rejected_count': properties.filter(status='rejected').count(),
        'sold_count': properties.filter(status='sold').count(),

        'query': query,
        'selected_status': selected_status,
    }

    return render(request, 'proedge/agent_dashboard.html', context)


@login_required
def seller_dashboard(request):
    user = request.user
    query = request.GET.get('q')
    selected_status = request.GET.get('status')
    sort_by = request.GET.get('sort')
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    incomplete_profile = not profile.contact_number or not profile.profile_picture

    
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
    # Interest/offers for this seller’s properties
    # This assumes you have an Interest model that relates to Property and User    
    interests = Interest.objects.filter(property__seller=user).select_related('user', 'property')
    
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
        'properties': Property.objects.filter(seller=request.user),
        'incomplete_profile': incomplete_profile,
        'interests': interests,
        
    }

    return render(request, 'proedge/seller_dashboard.html', context)

@login_required
def buyer_dashboard(request):
    query = request.GET.get('q')
    selected_status = request.GET.get('status')
    sort_by = request.GET.get('sort')

    all_properties = Property.objects.filter(buyer=request.user)
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

    # ✅ Handle Bid Submission
    if request.method == 'POST' and 'property_id' in request.POST:
        prop_id = request.POST.get('property_id')
        try:
            property_instance = Property.objects.get(id=prop_id)
        except Property.DoesNotExist:
            messages.error(request, "Property not found.")
            return redirect('buyer_dashboard')

        if property_instance.listing_type == 'auction':
            bid_form = BidForm(request.POST)
            if bid_form.is_valid():
                bid = bid_form.save(commit=False)
                bid.user = request.user
                bid.property = property_instance
                bid.save()
                messages.success(request, f"Your bid of R{bid.amount} was placed successfully.")
            else:
                messages.error(request, "There was an error placing your bid. Please try again.")
        else:
            messages.warning(request, "Bidding is only allowed on auction listings.")

        return redirect('buyer_dashboard')  # Prevent resubmission

    # ✅ Group by status
    grouped_properties = defaultdict(list)
    for prop in properties:
        grouped_properties[prop.status].append(prop)

    # ✅ Generate a BidForm for each auction property
    bid_forms = {
        prop.id: BidForm() for prop in properties if prop.listing_type == 'auction'
    }

    context = {
        'grouped_properties': dict(grouped_properties),
        'role': 'buyer',
        'total_listings': all_properties.count(),
        'approved_count': all_properties.filter(status='approved').count(),
        'rejected_count': all_properties.filter(status='rejected').count(),
        'pending_count': all_properties.filter(status='pending').count(),
        'sold_count': all_properties.filter(status='sold').count(),
        'available_count': all_properties.filter(status='available').count(),
        'selected_status': selected_status,
        'query': query,
        'user_name': request.user.get_full_name() or request.user.username,
        'bid_forms': bid_forms,
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
        'role': 'Landlord',
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
    all_properties = Property.objects.filter(tenant=request.user)

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
        'role': 'Tenant',
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
    if request.method == 'POST':
        property_form = BankPropertyForm(request.POST)
        listing_form = BankListingForm(request.POST)

        if property_form.is_valid() and listing_form.is_valid():
            bank_property = property_form.save(commit=False)
            bank_property.bank = request.user  # assuming the logged-in user is the bank
            bank_property.save()

            listing = listing_form.save(commit=False)
            listing.property = bank_property
            listing.save()

            return redirect('bank_dashboard')
    else:
        property_form = BankPropertyForm()
        listing_form = BankListingForm()

    # Get properties submitted by this bank
    bank_properties = BankProperty.objects.filter(bank=request.user)

    context = {
        'property_form': property_form,
        'listing_form': listing_form,
        'bank_properties': bank_properties
    }

    return render(request, 'proedge/bank_dashboard.html', context)

# This view handles the auctioneer dashboard
# It shows auctions managed by the auctioneer and allows them to manage bids
@login_required
def auctioneer_dashboard(request):
    properties = Property.objects.filter(auctioneer=request.user)
    #auctions = Auction.objects.filter(auctioneer=request.user).select_related('property')
    auctions = Auction.objects.filter(auctioneer=request.user)
    auction_data = []
    for auction in auctions:
        bids = Bid.objects.filter(auction=auction).order_by('-amount')
        highest_bid = bids.first()
        auction_data.append({
            'auction': auction,
            'property': auction.property,
            'bids': bids,
            'highest_bid': highest_bid
        })

    return render(request, 'proedge/auctioneer_dashboard.html', {
        'role': 'Auctioneer',
        'properties': properties,
        'auction_data': auction_data,
        'auctions': auctions,
    })
# Add similar ones for tenant, landlord, agent


# Login and Registration View
def login_register_view(request):
    login_form = AuthenticationForm()
    register_form = CustomUserCreationForm()

    if request.method == 'POST':
        if 'login_submit' in request.POST:
            login_form = AuthenticationForm(request, data=request.POST)
            if login_form.is_valid():
                login(request, login_form.get_user())
                return redirect('dashboard_redirect')
        elif 'register_submit' in request.POST:
            register_form = CustomUserCreationForm(request.POST)
            if register_form.is_valid():
                user = register_form.save()
                login(request, user)
                return redirect('dashboard_redirect')

    return render(request, 'proedge/login_register.html', {
        'login_form': login_form,
        'register_form': register_form
    })
    
@login_required
def edit_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('user_profile')
    else:
        form = EditProfileForm(instance=profile)

    return render(request, 'proedge/edit_profile.html', {'form': form})

#user profile view
@login_required
def user_profile_view(request):
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        return redirect('edit_profile')  # If no profile exists yet

    return render(request, 'proedge/user_profile.html', {'profile': profile})

# Interest messages view for agents, sellers, landlords, banks, auctioneers
@login_required
def interest_messages_view(request):
    user = request.user
    messages = Interest.objects.filter(property__agent=request.user).order_by('-created_at')
    interests = Interest.objects.filter(property__seller=user).select_related('user', 'property')
    
    # Filter messages based on user role
    if hasattr(user, 'agent'):
        interests = Interest.objects.filter(property__agent=user)
    elif hasattr(user, 'seller'):
        interests = Interest.objects.filter(property__seller=user)
    elif hasattr(user, 'landlord'):
        interests = Interest.objects.filter(property__landlord=user)
    elif hasattr(user, 'bank'):
        interests = Interest.objects.filter(property__bank=user)
    elif hasattr(user, 'auctioneer'):
        interests = Interest.objects.filter(property__auctioneer=user)
    else:
        interests = Interest.objects.filter(user=user)  # for buyers/tenants

    context = {
        'interests': interests.order_by('-created_at'),
        'messages': messages,
        'interests': interests,
    }
    return render(request, 'proedge/messages.html', context)


@login_required
def create_auction(request):
    if request.method == 'POST':
        form = AuctionForm(request.POST, user=request.user)
        if form.is_valid():
            auction = form.save(commit=False)

            # Get the property from cleaned_data
            selected_property = form.cleaned_data.get('property')
            if selected_property is None:
                form.add_error('property', 'Please select a valid property.')
            else:
                auction.property = selected_property
                auction.auctioneer = request.user
                auction.save()
                messages.success(request, 'Auction created successfully.')
                return redirect('auctioneer_dashboard')
    else:
        form = AuctionForm(user=request.user)

    return render(request, 'proedge/create_auction.html', {'form': form})

# This view handles the auction detail page
@login_required
def auction_detail(request, auction_id):
    auction = get_object_or_404(Auction, id=auction_id)
    property = auction.property  # This is correct
    bids = auction.bids.all()  # via related_name='bids'
    
    if request.method == 'POST':
        form = BidForm(request.POST)
        if form.is_valid():
            bid = form.save(commit=False)
            bid.auction = auction
            bid.bidder = request.user
            bid.save()
            messages.success(request, "Your bid was placed successfully.")
            return redirect('auction_detail', auction_id=auction.id)
    else:
        form = BidForm()

    return render(request, 'proedge/auction_detail.html', {
        'auction': auction,
        'form': form,
        'bids': bids,
    })
    #return render(request, 'proedge/auction_detail.html', {'auction': auction})
# This view allows auctioneers to edit an existing auction
# It uses the AuctionForm to handle the form submission
@login_required
def edit_auction(request, auction_id):
    auction = get_object_or_404(Auction, id=auction_id)

    if request.method == 'POST':
        form = AuctionForm(request.POST, instance=auction)
        if form.is_valid():
            form.save()
            return redirect('proedge:auction_detail', auction_id=auction.id)  # or your dashboard
    else:
        form = AuctionForm(instance=auction)  # <== pre-fill form

    return render(request, 'proedge/edit_auction.html', {'form': form, 'auction': auction})

# This view handles the agency dashboard
# It shows the agency's agents and properties, along with summary stats

@login_required
def agency_dashboard(request):
    """
    Dashboard for an Agency:
    - Shows all agents under this agency
    - Shows all properties listed by this agency (grouped by status)
    - Shows join requests with counts (pending, approved, rejected)
    """
    # ✅ Make sure this user actually owns an agency
    try:
        agency = request.user.agency_profile  
    except Agency.DoesNotExist:
        return redirect("create_agency_profile")

    # ✅ Get all properties linked to this agency
    properties = Property.objects.filter(agency=agency).order_by("-created_at")

    # ✅ Group properties by status for template display
    grouped_properties = defaultdict(list)
    for prop in properties:
        grouped_properties[prop.status].append(prop)

    # ✅ Get all agents linked to this agency
    agents = AgentProfile.objects.filter(agency=agency)

    # ✅ Get all join requests
    join_requests = AgentJoinRequest.objects.filter(agency=agency).order_by("-created_at")

    # ✅ Count join request statuses
    pending_requests_count = join_requests.filter(is_approved=False).count()
    approved_requests_count = join_requests.filter(is_approved=True).count()
    rejected_requests_count = join_requests.filter(is_approved=False).exclude(is_approved=None).count()

    context = {
        "agency": agency,
        "properties": properties,
        "grouped_properties": dict(grouped_properties),
        "agents": agents,
        "join_requests": join_requests,
        "pending_requests_count": pending_requests_count,
        "approved_requests_count": approved_requests_count,
        "rejected_requests_count": rejected_requests_count,
    }

    return render(request, "proedge/agency_dashboard.html", context)

@login_required
def agent_join_request_detail(request, request_id):
    join_request = get_object_or_404(AgentJoinRequest, id=request_id)

    documents = join_request.documents.all()

    return render(request, 'proedge/agent_join_request_detail.html', {
        'join_request': join_request,
        'documents': documents,
    })
   
# This view allows users to create a new agency
@login_required
def complete_agency_profile(request):
    if hasattr(request.user, 'agency_profile'):
        return redirect('agency_dashboard')  # Already completed

    if request.method == 'POST':
        form = AgencyForm(request.POST, request.FILES)
        if form.is_valid():
            agency = form.save(commit=False)
            agency.owner = request.user
            agency.save()
            return redirect('agency_dashboard')
    else:
        form = AgencyForm()

    return render(request, 'proedge/complete_profile.html', {'form': form})

    
    
@login_required
def request_join_agency(request):
    AgentDocumentFormSet = modelformset_factory(
        AgentDocument, form=AgentDocumentForm, extra=2, max_num=5, validate_max=True
    )

    if request.method == 'POST':
        form = AgentJoinRequestForm(request.POST)
        formset = AgentDocumentFormSet(request.POST, request.FILES, queryset=AgentDocument.objects.none())

        if form.is_valid() and formset.is_valid():
            join_request = form.save(commit=False)
            join_request.agent = request.user
            join_request.save()

            # Save docs and run the automated verification per doc
            for doc_form in formset:
                if not doc_form.cleaned_data:
                    continue
                doc = doc_form.save(commit=False)
                doc.join_request = join_request
                doc.save()
                automated_verify_agent_document(doc)

            # Summarize auto-check results
            docs = list(join_request.documents.all())
            rejected = [d for d in docs if d.status == 'rejected']
            approved = [d for d in docs if d.status == 'approved']

            if rejected:
                join_request.auto_check_status = 'failed'
                reasons = [f"{d.document_type}: {d.rejection_reason}" for d in rejected]
                join_request.auto_check_notes = "Auto-check failed. " + " | ".join(reasons)
            else:
                join_request.auto_check_status = 'passed'
                join_request.auto_check_notes = f"Auto-check passed. {len(approved)} document(s) valid."

            join_request.save()

            # Notify the agency by email
            summary = join_request.auto_check_notes or "Agent submitted a new join request."
            notify_agency_new_join_request(join_request, summary)

            messages.success(request, "Your join request and documents were submitted.")
            return redirect('agent_dashboard')
    else:
        form = AgentJoinRequestForm()
        formset = AgentDocumentFormSet(queryset=AgentDocument.objects.none())

    return render(request, 'proedge/request_join_agency.html', {'form': form, 'formset': formset})
    


# Reject join request view
@login_required
def reject_join_request(request, request_id):
    join_request = get_object_or_404(AgentJoinRequest, id=request_id, is_approved=False)

    # Optionally fetch document rejection reasons if you want to include
    docs = join_request.agent.agentdocument_set.filter(status='rejected')
    reasons = "\n".join([f"{doc.get_document_type_display}: {doc.rejection_reason}" for doc in docs])

    # Send rejection email to agent
    send_mail(
        subject="Your join request has been rejected",
        message=f"Hi {join_request.agent.get_full_name() or join_request.agent.username},\n\n"
                f"Unfortunately, your request to join the agency '{join_request.agency.name}' was rejected.\n"
                f"Reasons:\n{reasons if reasons else 'No specific reasons provided.'}\n\n"
                "Please contact the agency for more details.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[join_request.agent.email],
        fail_silently=True,
    )


    # keep record, add a manual reason if you capture it in a form
    manual_reason = request.POST.get('reason', '').strip()
    if manual_reason:
        join_request.manual_rejection_reason = manual_reason
        join_request.save()
    else:
        # if you still want to delete, it’s fine—but then you can’t show history later
        # join_request.delete()
        # Instead, mark as “failed”
        join_request.auto_check_status = 'failed'
        join_request.auto_check_notes = 'Rejected by agency (no reason provided).'
        join_request.save()

        # Notify agent
    notify(
        join_request.agent,
        title="Your agency join request was rejected",
        message=join_request.manual_rejection_reason or "Please contact the agency for more details."
    )

    join_request.delete()
    messages.success(request, "Agent join request rejected.")
    return redirect('agency_dashboard')


@login_required
def notifications_list(request):
    qs = request.user.notifications.all()
    paginator = Paginator(qs, 15)
    page = request.GET.get('page')
    notifications = paginator.get_page(page)
    return render(request, 'proedge/notifications.html', {'notifications': notifications})


@login_required
def manual_approve_document(request, doc_id):
    document = get_object_or_404(AgentDocument, id=doc_id)
    # Update status to approved, clear rejection reason, mark automated_checked True
    document.status = 'approved'
    document.rejection_reason = ''
    document.automated_checked = True
    document.save()

    # Update overall join request status
    update_join_request_auto_status(document.join_request)

    messages.success(request, f"Document {document.document_type} approved manually.")
    return redirect('agency_dashboard')

@login_required
def manual_reject_document(request, doc_id):
    document = get_object_or_404(AgentDocument, id=doc_id)

    if request.method == 'POST':
        reason = request.POST.get('reason')
        if not reason:
            messages.error(request, "Please provide a rejection reason.")
            return redirect('view_agent_document', doc_id=doc_id)

        document.status = 'rejected'
        document.rejection_reason = reason
        document.automated_checked = True
        document.save()

        # Update overall join request status
        update_join_request_auto_status(document.join_request)

        messages.success(request, f"Document {document.document_type} rejected manually.")
        return redirect('agency_dashboard')
    else:
        # Render a simple form for rejection reason
        return render(request, 'proedge/manual_reject_document.html', {'document': document})

def update_join_request_auto_status(join_request):
    docs = list(join_request.documents.all())
    rejected = [d for d in docs if d.status == 'rejected']
    approved = [d for d in docs if d.status == 'approved']

    if rejected:
        join_request.auto_check_status = 'failed'
        reasons = [f"{d.document_type}: {d.rejection_reason}" for d in rejected]
        join_request.auto_check_notes = "Manual check failed. " + " | ".join(reasons)
    else:
        join_request.auto_check_status = 'passed'
        join_request.auto_check_notes = f"Manual check passed. {len(approved)} document(s) valid."

    join_request.save()



@login_required
def approve_join_request(request, request_id):
    join_request = get_object_or_404(AgentJoinRequest, id=request_id, is_approved=False)

    join_request.is_approved = True
    join_request.save()

    agent_profile = AgentProfile.objects.get(user=join_request.agent)
    agent_profile.agency = join_request.agency
    agent_profile.save()

    # Send approval email to agent
    send_mail(
        subject="Your join request has been approved",
        message=f"Hi {join_request.agent.get_full_name() or join_request.agent.username},\n\n"
                f"Your request to join the agency '{join_request.agency.name}' has been approved. Welcome aboard!",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[join_request.agent.email],
        fail_silently=True,
    )

    # Notify agent
    notify(
        join_request.agent,
        title="Your agency join request was approved 🎉",
        message=f"{join_request.agency.name} approved your request."
    )
    
    messages.success(request, f"{join_request.agent.username} has been approved and added to your agency.")
    return redirect('agency_dashboard')


# This view allows agency owners to edit their agency profile
@login_required
def edit_agency_profile(request):
    agency = get_object_or_404(Agency, owner=request.user)

    if request.method == 'POST':
        form = AgencyForm(request.POST, request.FILES, instance=agency)
        if form.is_valid():
            form.save()
            messages.success(request, 'Agency profile updated successfully.')
            return redirect('agency_dashboard')
    else:
        form = AgencyForm(instance=agency)

    return render(request, 'proedge/edit_agency_profile.html', {'form': form})


@login_required
def edit_agent_profile(request, pk):
    agent = get_object_or_404(CustomUser, pk=pk, role='agent')
    profile = get_object_or_404(UserProfile, user=agent)

    if request.user.agency_profile != profile.agency:
        return redirect('agency_dashboard')

    if request.method == 'POST':
        form = AgencyCreateAgentForm(request.POST, request.FILES, instance=agent)
        if form.is_valid():
            form.save(agency=request.user.agency_profile)
            messages.success(request, "Agent profile updated successfully!")
            return redirect('edit_agent_profile', pk=agent.pk)
    else:
        form = AgencyCreateAgentForm(instance=agent)

    return render(request, 'proedge/edit_agent_profile.html', {
        'agent': agent,
        'profile': profile,
        'form': form
    })

# This view allows agency owners to view their agency profile
@login_required
def view_agency_profile(request):
    agency = get_object_or_404(Agency, owner=request.user)
    return render(request, 'proedge/view_agency_profile.html', {
        'agency': agency
    })

# Handle agent join request actions
@login_required
def handle_join_request(request, request_id):
    join_request = get_object_or_404(AgentJoinRequest, id=request_id, is_approved=False)

    action = request.POST.get('action')
    reason = request.POST.get('reason', '')  # add a textarea in your form if you want to capture this

    if action == 'approve':
        join_request.is_approved = True
        join_request.save()

        # Attach agent to agency (your existing behavior)
        agent_profile = AgentProfile.objects.get(user=join_request.agent)
        agent_profile.agency = join_request.agency
        agent_profile.save()

        # Email agent
        notify_agent_request_decision(join_request, approved=True)

        messages.success(request, "Agent approved.")
    elif action == 'reject':
        # Instead of delete, keep a record & email agent (or keep your delete if you prefer)
        # join_request.delete()  # if you really want to delete
        notify_agent_request_decision(join_request, approved=False, reason=reason or "Not specified.")
        messages.success(request, "Agent rejected.")

    return redirect('agency_dashboard')

# This view handles user logout
def custom_logout(request):
    logout(request)
    return redirect('login')  # or wherever you want to go after logout


#add bank_property view
@login_required
def add_bank_property(request):
    if request.method == 'POST':
        form = BankPropertyForm(request.POST)
        listing_form = BankListingForm(request.POST)

        if form.is_valid() and listing_form.is_valid():
            bank_property = form.save(commit=False)
            bank_property.bank = request.user  # Assuming `bank` is the user
            bank_property.save()

            listing = listing_form.save(commit=False)
            listing.property = bank_property
            listing.save()

            messages.success(request, "Bank property submitted successfully.")
            return redirect('bank_dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = BankPropertyForm()
        listing_form = BankListingForm()

    return render(request, 'bankdashboard/submit_bank_property.html', {
        'form': form,
        'listing_form': listing_form,
    })


