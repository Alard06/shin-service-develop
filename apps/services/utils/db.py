from asgiref.sync import sync_to_async

from apps.services.models import UniqueDetail, UniqueProductNoPhoto
from apps.suppliers.models import Tire, TireSupplier, TruckTire, TruckTireSupplier, SpecialTire, SpecialTireSupplier, \
    MotoTire, MotoTireSupplier, Disk, DiskSupplier, TruckDisk, TruckDiskSupplier
from django.db import transaction

@sync_to_async
def get_tire_objects(**tire_data):
    return Tire.objects.get_or_create(**tire_data)


@sync_to_async
def get_truck_objects(**truck_data):
    return TruckTire.objects.get_or_create(**truck_data)


@sync_to_async
def get_special_tire_objects(**special_tire_data):
    return SpecialTire.objects.get_or_create(**special_tire_data)


@sync_to_async
def get_moto_tire_objects(**moto_tire_data):
    return MotoTire.objects.get_or_create(**moto_tire_data)


@sync_to_async
def get_disk_elements_objects(**disk_elements_data):
    return Disk.objects.get_or_create(**disk_elements_data)


@sync_to_async
def get_trucks_disks_objects(**trucks_disks_data):
    return TruckDisk.objects.get_or_create(trucks_disks_data)


@sync_to_async
def bulk_create_tires(tire_data_list):
    """Bulk create tire objects efficiently."""
    new_tires = [Tire(**tire_data) for tire_data in tire_data_list]
    if new_tires:
        with transaction.atomic():
            created_tires = Tire.objects.bulk_create(new_tires)
    else:
        created_tires = []
    return created_tires


@sync_to_async
def bulk_create_disks(disk_data_list):
    """Bulk create disk objects efficiently."""
    new_disks = [Disk(**disk_data) for disk_data in disk_data_list]
    if new_disks:
        with transaction.atomic():
            created_disks = Disk.objects.bulk_create(new_disks)
    else:
        created_disks = []
    return created_disks


@sync_to_async
def bulk_create_truck_tires(truck_tire_data_list):
    """Bulk create truck tire objects efficiently."""
    new_truck_tires = [TruckTire(**truck_tire_data) for truck_tire_data in truck_tire_data_list]
    if new_truck_tires:
        with transaction.atomic():
            created_truck_tires = TruckTire.objects.bulk_create(new_truck_tires)
    else:
        created_truck_tires = []
    return created_truck_tires

@sync_to_async
def bulk_create_special_tires(special_tire_data_list):
    """Bulk create special tire objects efficiently."""
    new_special_tires = [SpecialTire(**special_tire_data) for special_tire_data in special_tire_data_list]
    if new_special_tires:
        with transaction.atomic():
            created_special_tires = SpecialTire.objects.bulk_create(new_special_tires)
    else:
        created_special_tires = []
    return created_special_tires

@sync_to_async
def bulk_create_moto_tires(moto_tire_data_list):
    """Bulk create motorcycle tire objects efficiently."""
    new_moto_tires = [MotoTire(**moto_tire_data) for moto_tire_data in moto_tire_data_list]
    if new_moto_tires:
        with transaction.atomic():
            created_moto_tires = MotoTire.objects.bulk_create(new_moto_tires)
    else:
        created_moto_tires = []
    return created_moto_tires

@sync_to_async
def bulk_create_truck_disks(disk_data_list):
    """Bulk create truck disk objects efficiently."""
    new_disks = [TruckDisk(**disk_data) for disk_data in disk_data_list]
    if new_disks:
        with transaction.atomic():
            created_disks = TruckDisk.objects.bulk_create(new_disks)
    else:
        created_disks = []
    return created_disks
@sync_to_async
def tire_supplier_bulk_create(tire_data):
    TireSupplier.objects.bulk_create(tire_data)


@sync_to_async
def truck_tire_supplier_bulk_create(tire_data):
    TruckTireSupplier.objects.bulk_create(tire_data)


@sync_to_async
def special_tire_supplier_bulk_create(special_tire_data):
    return SpecialTireSupplier.objects.bulk_create(special_tire_data)


@sync_to_async
def moto_tire_supplier_bulk_create(moto_tire_data):
 MotoTireSupplier.objects.bulk_create(moto_tire_data)


@sync_to_async
def disk_supplier_bulk_create(disk_elements_data):
    DiskSupplier.objects.bulk_create(disk_elements_data)


@sync_to_async
def trucks_disks_supplier_bulk_create(trucks_disks_data):
    TruckDiskSupplier.objects.bulk_create(trucks_disks_data)


def add_unique_product_no_photo(pk, tires_element):
    unique_detail = UniqueDetail.objects.get(pk=pk)
    new_product = UniqueProductNoPhoto.objects.create(
        id_product=tires_element.get('id'),
        brand=tires_element.get('brand'),
        product=tires_element.get('product')
    )
    unique_detail.products.add(new_product)  # Use add() to associate the new product
    unique_detail.save()