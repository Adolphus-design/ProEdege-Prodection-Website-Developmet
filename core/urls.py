from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # Main pages
    path('', include(('proedge.urls', 'proedge'), namespace='proedge')),

    # Listings
    path('listings/', include(('listings.urls', 'listings'), namespace='listings')),
    path('properties/', include(('listings.urls', 'listings'))),  # alias route

    # Staff
    path('staff/', include(('staff.urls', 'staff'), namespace='staff')),

    # Admin panel
    path('adminpanel/', include(('adminpanel.urls', 'adminpanel'), namespace='adminpanel')),

    # Agency listings
    path('agency/', include(('agencylistings.urls', 'agencylistings'), namespace='agencylistings')),

    # Bank dashboard (uncomment if ready)
    # path('bankdashboard/', include(('bankdashboard.urls', 'bankdashboard'), namespace='bankdashboard')),
]

# Serve media files even in production (temporary for Render)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
