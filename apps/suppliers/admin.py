from django.contrib import admin

from .models import Supplier, City, CompanySupplier, Tire, TireSupplier, MotoTireSupplier, MotoTire, SpecialTire, \
    SpecialTireSupplier, TruckTireSupplier, TruckTire, Disk, DiskSupplier, TruckDisk, TruckDiskSupplier, TireCompany, \
    DiskCompany, SpecialTireCompany, MotoTireCompany, TruckDiskCompany, TruckTireCompany

# Register your models here.
admin.site.register(Supplier)
admin.site.register(City)
admin.site.register(CompanySupplier)
admin.site.register(Tire)
admin.site.register(TireSupplier)
admin.site.register(MotoTire)
admin.site.register(MotoTireSupplier)
admin.site.register(SpecialTire)
admin.site.register(SpecialTireSupplier)
admin.site.register(TruckTire)
admin.site.register(TruckTireSupplier)
admin.site.register(Disk)
admin.site.register(TruckDisk)
admin.site.register(TruckDiskSupplier)
admin.site.register(TireCompany)
admin.site.register(DiskCompany)
admin.site.register(SpecialTireCompany)
admin.site.register(MotoTireCompany)
admin.site.register(TruckDiskCompany)
admin.site.register(TruckTireCompany)
@admin.register(DiskSupplier)
class DiskSupplierAdmin(admin.ModelAdmin):
    search_fields = ['disk__product', 'supplier__name', 'articul']  # Поля для поиска
