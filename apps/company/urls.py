from django.urls import path

from .views import company_list, create_company, company_detail, add_suppliers_to_company, delete_supplier_company, \
    delete_company, edit_company, company_data, run_uniqueness_checker, delete_file, upload_file_company, \
    download_file_unique, update_company_settings, save_ad_order, sortable_ad_view

urlpatterns = [
    path('companies/', company_list, name='company_list'),
    path('companies/create/', create_company, name='create_company'),
    path('companies/<int:company_id>/', company_detail, name='company_detail'),
    path('companies/<int:company_id>/add-suppliers/', add_suppliers_to_company, name='add_suppliers_to_company'),
    path('supplier/delete/<int:supplier_id>/company/<int:company_id>/', delete_supplier_company,
         name='delete_supplier_company'),
    path('companies/<int:company_id>/edit/', edit_company, name='edit_company'),
    path('companies/<int:company_id>/delete/', delete_company, name='delete_company'),
    path('companies/<int:company_id>/data/', company_data, name='company_data'),
    path('run_uniqueness_checker/<int:company_id>', run_uniqueness_checker, name='run_uniqueness_checker'),
    path('delete_file/<int:company_id>', delete_file, name='delete_file'),
    path('upload_file/<int:company_id>/', upload_file_company, name='upload_file_company'),
    path('download_file/', download_file_unique, name='download_file'),
    path('company/<int:company_id>/settings/', update_company_settings, name='update_company_settings'),
    path('company/<int:company_id>/ad-order/', save_ad_order, name='save_ad_order'),
    path('company/<int:company_id>/sortable-ad/', sortable_ad_view, name='sortable_ad'),
]
