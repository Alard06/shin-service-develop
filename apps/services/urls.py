from django.urls import path
from django.views.generic import TemplateView

from .views import upload_file, services_index, list_files, delete_file, upload_suppliers, UploadDataView

urlpatterns = [
    path('services/upload/', upload_file, name='upload_file'),
    path('services/upload/success/', TemplateView.as_view(template_name='upload_success.html'), name='upload_success'),
    path('services/', list_files, name='list_files'),
    path('services/delete-file/', delete_file, name='delete_file'),
    path('upload-suppliers/', upload_suppliers, name='upload_suppliers'),
    path('upload-data/', UploadDataView.as_view(), name='upload_data'),
]