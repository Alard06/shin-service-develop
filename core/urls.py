
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.suppliers.urls')),
    path('', include('apps.services.urls')),
    path('', include('apps.index.urls')),
    path('', include('apps.company.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
