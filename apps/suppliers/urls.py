from django.urls import path

from apps.suppliers.views import create_supplier, edit_company_supplier, delete_supplier, supplier_detail, supplier_list, \
    add_suppliers_to_company, edit_supplier

urlpatterns = [
    path('suppliers/', supplier_list, name='supplier_list'),
    path('create/', create_supplier, name='create_supplier'),
    path('edit_supplier/<int:supplier_id>/', edit_supplier, name='edit_supplier'),
    path('supplier/<int:company_supplier_id>/edit/', edit_company_supplier, name='edit_company_supplier'),
    path('delete/<int:supplier_id>/', delete_supplier, name='delete_supplier'),
    path('suppliers/<int:supplier_id>/', supplier_detail, name='supplier_detail'),
    path('company/<int:company_id>/add-suppliers/', add_suppliers_to_company, name='add_suppliers_to_company'),
]
