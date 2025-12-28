from django.contrib import admin
from django.urls import path, include
from accounts import views
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = "Labang Online Admin"
admin.site.site_title = "Labang Online Admin Portal"
admin.site.index_title = "Welcome to Labang Online Administration"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('accounts/', include('accounts.urls')),
    path('certificates/', include('certificates.urls')),
    path('reports/', include('reports.urls')),
    path('announcements/', include('announcements.urls')),
    path('administration/', include('administration.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)