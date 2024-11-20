from django.urls import path

from .views import company_list, create_company, company_detail, add_suppliers_to_company, delete_supplier_company, \
    delete_company, edit_company, company_data, run_uniqueness_checker, delete_file, upload_file_company, \
    download_file_unique, save_ad_order, sortable_ad_view, uniq_drom_settings, \
    update_company_drom_settings, uniq_avito_settings, update_company_avito_settings, uniq_xlsx_settings, \
    company_brand_exceptions, company_brand_exceptions_data, sortable_ad_view_avito, save_ad_order_avito, load_photo, \
    result_uniq

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
    path('company/<int:company_id>/settings/drom/', update_company_drom_settings, name='update_company_drom_settings'),
    path('company/<int:company_id>/settings/avito/', update_company_avito_settings, name='update_company_avito_settings'),
    path('company/<int:company_id>/ad-order/drom/', save_ad_order, name='save_ad_order'),
    path('company/<int:company_id>/ad-order/avito/', save_ad_order_avito, name='save_ad_order_avito'),
    path('company/<int:company_id>/sortable-ad/drom', sortable_ad_view, name='sortable_ad'),
    path('company/<int:company_id>/sortable-ad/avito', sortable_ad_view_avito, name='sortable_ad_avito'),
    path('company/<int:company_id>/uniq/drom/', uniq_drom_settings, name='uniq_drom_settings'),
    path('company/<int:company_id>/uniq/avito/', uniq_avito_settings, name='uniq_avito_settings'),
    path('company/<int:company_id>/uniq/xlsx/', uniq_xlsx_settings, name='uniq_xlsx_settings'),
    path('company/<int:company_id>/exceptions/', company_brand_exceptions, name='company_brand_exceptions'),
    path('company/<int:company_id>/exceptions/data', company_brand_exceptions_data, name='company_brand_exceptions_data'),
    path('company/<int:company_id>/load/photo', load_photo, name='load_photo_company'),
    path('company/<int:company_id>/result-uniq/<int:uniq_data_id>', result_uniq, name='result_uniq'),

]
