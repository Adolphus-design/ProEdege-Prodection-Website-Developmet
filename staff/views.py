from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from listings.models import Property
from django.contrib.auth import get_user_model

User = get_user_model()

def is_staff_user(user):
    return user.is_authenticated and user.is_staff

@login_required
@user_passes_test(is_staff_user)
def dashboard(request):
    properties = Property.objects.all()
    users = User.objects.all()
    return render(request, 'staff/dashboard.html', {
        'properties': properties,
        'users': users,
    })
