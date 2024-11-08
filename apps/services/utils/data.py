from django.utils import timezone
import xml.etree.ElementTree as ET
from asgiref.sync import sync_to_async

from apps.services.utils.db import get_tire_objects, tire_supplier_bulk_create, get_truck_objects, \
    truck_tire_supplier_bulk_create, get_special_tire_objects, special_tire_supplier_bulk_create, get_moto_tire_objects, \
    moto_tire_supplier_bulk_create, get_disk_elements_objects, disk_supplier_bulk_create, get_trucks_disks_objects, \
    trucks_disks_supplier_bulk_create, bulk_create_tires, bulk_create_truck_disks, bulk_create_disks, \
    bulk_create_truck_tires, bulk_create_special_tires, bulk_create_moto_tires
from apps.suppliers.models import TireSupplier, Tire, DiskSupplier, Disk, TruckTireSupplier, TruckTire, \
    SpecialTireSupplier, SpecialTire, MotoTireSupplier, MotoTire, TruckDisk, TruckDiskSupplier

from lxml import etree
import time


async def tires_elements(suppliers, cities, file_path):
    print('tires_elements')
    tire_suppliers_to_create = []
    tire_data_list = []
    tire_objects = {}

    # Start timing the overall execution
    overall_start_time = time.time()

    # Use lxml for faster parsing
    parse_start_time = time.time()
    for event, elem in etree.iterparse(file_path, events=('end',), tag='tire'):
        tire_data = {
            'id_tire': elem.get('id'),
            'brand': elem.get('brand'),
            'brand_article': elem.get('brandArticul'),
            'product': elem.get('product'),
            'image': elem.get('image'),
            'full_title': elem.get('fullTitle'),
            'model': elem.get('model'),
            'season': elem.get('season'),
            'spike': elem.get('spike') == 'да',
            'runflat': elem.get('runflat') == 'да',
            'lightduty': elem.get('lightduty') == 'да',
            'indexes': elem.get('indexes'),
            'width': elem.get('width'),
            'height': elem.get('height'),
            'diameter': elem.get('diameter'),
            'system': elem.get('system'),
            'omolagation': elem.get('omolagation'),
            'mud': elem.get('mud'),
            'at': elem.get('at'),
            'runFlatTitle': elem.get('runFlatTitle'),
            'fr': elem.get('fr'),
            'xl': elem.get('xl')
        }

        # Add tire data to the list if the full title is present
        if tire_data['full_title']:
            tire_data_list.append(tire_data)

        # Process suppliers for this tire
        for supplier in elem.findall('supplier'):
            articul = supplier.get('articul')
            price = supplier.get('price')
            input_price = supplier.get('inputPrice')
            quantity = supplier.get('quantity')
            supplier_title = supplier.get('supplierTitle')
            city_name = supplier.get('city')
            presence = supplier.get('presence')
            delivery_period_days = supplier.get('deliveryPeriodDays')
            last_availability_date = supplier.get('lastAvailabilityDate')
            sale = supplier.get('sale') == 'yes'

            last_availability_date_aware = (
                timezone.make_aware(
                    timezone.datetime.strptime(last_availability_date, '%d.%m.%Y %H:%M:%S')
                ) if last_availability_date else None
            )

            supplier_obj = suppliers.get(supplier_title)
            city_obj = cities.get(city_name)

            # Create supplier data only if the supplier and city objects exist
            if supplier_obj and city_obj:
                tire_suppliers_to_create.append(
                    {
                        'articul': articul,
                        'price': price,
                        'input_price': input_price,
                        'quantity': quantity,
                        'supplier': supplier_obj,
                        'city': city_obj,
                        'presence': presence,
                        'delivery_period_days': delivery_period_days,
                        'last_availability_date': last_availability_date_aware,
                        'sale': sale,
                        'tire_full_title': tire_data['full_title']  # Store tire title for later mapping
                    }
                )

        elem.clear()  # Clear the element to free memory

    # After parsing, create tire objects in bulk
    tire_objects_created = await bulk_create_tires(tire_data_list)

    # Map created tire objects for easy access
    for tire_obj in tire_objects_created:
        if tire_obj:
            tire_objects[tire_obj.full_title] = tire_obj

    # Prepare supplier objects for bulk creation
    suppliers_to_create = []
    for supplier_data in tire_suppliers_to_create:
        tire_obj = tire_objects.get(supplier_data['tire_full_title'])
        if tire_obj:
            suppliers_to_create.append(
                TireSupplier(
                    tire=tire_obj,
                    articul=supplier_data['articul'],
                    price=supplier_data['price'],
                    input_price=supplier_data['input_price'],
                    quantity=supplier_data['quantity'],
                    supplier=supplier_data['supplier'],
                    city=supplier_data['city'],
                    presence=supplier_data['presence'],
                    delivery_period_days=supplier_data['delivery_period_days'],
                    last_availability_date=supplier_data['last_availability_date'],
                    sale=supplier_data['sale']
                )
            )

    # Bulk create suppliers
    if suppliers_to_create:
        batch_size = 1000
        batch_creation_start_time = time.time()
        for i in range(0, len(suppliers_to_create), batch_size):
            batch = suppliers_to_create[i:i + batch_size]
            try:
                await tire_supplier_bulk_create(batch)
                print('Batch of suppliers created')
            except Exception as e:
                print(f'Error creating batch of suppliers: {e}')
        batch_creation_end_time = time.time()
        print(f'Batch creation time: {batch_creation_end_time - batch_creation_start_time:.2f} seconds')

    overall_end_time = time.time()
    print(f'Overall execution time: {overall_end_time - overall_start_time:.2f} seconds')
    print('TIRE OK')


from decimal import Decimal, InvalidOperation


async def safe_decimal_conversion(value):
    if value:
        try:
            # Replace comma with period for decimal conversion
            return Decimal(value.replace(',', '.'))
        except InvalidOperation:
            return Decimal('0.00')  # Default value if conversion fails
    return Decimal('0.00')  # Default value for empty strings


async def trucks_disks_elements(suppliers, cities, root):
    print('truck disks')
    disks_element = root.find('truckDisks')
    if disks_element is not None:
        disk_suppliers_to_create = []
        disk_data_list = []
        disk_objects = {}

        # Collect data about disks
        for disk in disks_element.findall('truckDisk'):
            disk_data = {
                'id_disk': disk.get('id'),
                'brand_articul': disk.get('brandArticul'),
                'brand': disk.get('brand'),
                'product': disk.get('product'),
                'image': disk.get('image'),
                'full_title': disk.get('fullTitle'),
                'model': disk.get('model'),
                'pcd': disk.get('pcd'),
                'outfit': disk.get('outfit'),
                'color': disk.get('color'),
                'type': disk.get('type'),
                'width': disk.get('width'),
                'diameter': disk.get('diameter'),
                'boltcount': disk.get('boltcount'),
                'dia': disk.get('dia'),
            }

            # Add disk data to the list if the full title is present
            if disk_data['full_title']:
                disk_data_list.append(disk_data)

        # After collecting all disk data, create disk objects in bulk
        disk_objects_created = await bulk_create_truck_disks(disk_data_list)

        # Map created disk objects for easy access
        for disk_obj in disk_objects_created:
            if disk_obj:
                disk_objects[disk_obj.full_title] = disk_obj

        # Process suppliers for each disk
        for disk in disks_element.findall('truckDisk'):
            disk_full_title = disk.get('fullTitle')
            disk_obj = disk_objects.get(disk_full_title)

            for supplier in disk.findall('supplier'):
                articul = supplier.get('articul')
                price = supplier.get('price')
                input_price = supplier.get('inputPrice')
                quantity = supplier.get('quantity')
                supplier_title = supplier.get('supplierTitle')
                city_name = supplier.get('city')
                presence = supplier.get('presence')
                delivery_period_days = supplier.get('deliveryPeriodDays')
                last_availability_date = supplier.get('lastAvailabilityDate')
                sale = supplier.get('sale') == 'yes'

                # Convert date to timezone-aware datetime
                last_availability_date_aware = None
                if last_availability_date:
                    last_availability_date_aware = timezone.make_aware(
                        timezone.datetime.strptime(last_availability_date, '%d.%m.%Y %H:%M:%S')
                    )

                supplier_obj = suppliers.get(supplier_title)
                city_obj = cities.get(city_name)

                if supplier_obj and city_obj and disk_obj:
                    disk_suppliers_to_create.append(
                        TruckDiskSupplier(
                            truck_disk=disk_obj,
                            articul=articul,
                            price=price,
                            input_price=input_price,
                            quantity=quantity,
                            supplier=supplier_obj,
                            city=city_obj,
                            presence=presence,
                            delivery_period_days=delivery_period_days,
                            last_availability_date=last_availability_date_aware,
                            sale=sale
                        )
                    )

        # Bulk create all DiskSupplier instances at once
        if disk_suppliers_to_create:
            batch_size = 1000  # Adjust batch size as needed
            for i in range(0, len(disk_suppliers_to_create), batch_size):
                batch = disk_suppliers_to_create[i:i + batch_size]
                try:
                    await trucks_disks_supplier_bulk_create(batch)
                    print(f'Batch of {len(batch)} suppliers created successfully.')
                except Exception as e:
                    print(f'Error creating batch of suppliers: {e}')

        print('TRUCK DISK OK')


async def disks_elements(suppliers, cities, root):
    print('disks_elements')
    disks_element = root.find('disks')
    if disks_element is not None:
        disk_suppliers_to_create = []
        disk_data_list = []
        disk_objects = {}

        # Collect data about disks
        for disk in disks_element.findall('disk'):
            disk_data = {
                'id_disk': disk.get('id'),
                'brand_articul': disk.get('brandArticul'),
                'brand': disk.get('brand'),
                'product': disk.get('product'),
                'image': disk.get('image'),
                'full_title': disk.get('fullTitle'),
                'model': disk.get('model'),
                'pcd': disk.get('pcd'),
                'outfit': disk.get('outfit'),
                'color': disk.get('color'),
                'type': disk.get('type'),
                'width': disk.get('width'),
                'diameter': disk.get('diameter'),
                'boltcount': disk.get('boltcount'),
                'dia': disk.get('dia'),
            }

            # Add disk data to the list if the full title is present
            if disk_data['full_title']:
                disk_data_list.append(disk_data)

        # After collecting all disk data, create disk objects in bulk
        disk_objects_created = await bulk_create_disks(disk_data_list)

        # Map created disk objects for easy access
        for disk_obj in disk_objects_created:
            if disk_obj:
                disk_objects[disk_obj.full_title] = disk_obj

        # Process suppliers for each disk
        for disk in disks_element.findall('disk'):
            disk_full_title = disk.get('fullTitle')
            disk_obj = disk_objects.get(disk_full_title)

            for supplier in disk.findall('supplier'):
                articul = supplier.get('articul')
                price = supplier.get('price')
                input_price = supplier.get('inputPrice')
                quantity = supplier.get('quantity')
                supplier_title = supplier.get('supplierTitle')
                city_name = supplier.get('city')
                presence = supplier.get('presence')
                delivery_period_days = supplier.get('deliveryPeriodDays')
                last_availability_date = supplier.get('lastAvailabilityDate')
                sale = supplier.get('sale') == 'yes'

                # Convert date to timezone-aware datetime
                last_availability_date_aware = None
                if last_availability_date:
                    last_availability_date_aware = timezone.make_aware(
                        timezone.datetime.strptime(last_availability_date, '%d.%m.%Y %H:%M:%S')
                    )

                supplier_obj = suppliers.get(supplier_title)
                city_obj = cities.get(city_name)

                if supplier_obj and city_obj and disk_obj:
                    disk_suppliers_to_create.append(
                        DiskSupplier(
                            disk=disk_obj,
                            articul=articul,
                            price=price,
                            input_price=input_price,
                            quantity=quantity,
                            supplier=supplier_obj,
                            city=city_obj,
                            presence=presence,
                            delivery_period_days=delivery_period_days,
                            last_availability_date=last_availability_date_aware,
                            sale=sale
                        )
                    )

        # Bulk create all DiskSupplier instances at once
        if disk_suppliers_to_create:
            batch_size = 1000  # Adjust batch size as needed
            for i in range(0, len(disk_suppliers_to_create), batch_size):
                batch = disk_suppliers_to_create[i:i + batch_size]
                try:
                    await disk_supplier_bulk_create(batch)
                    print(f'Batch of {len(batch)} suppliers created successfully.')
                except Exception as e:
                    print(f'Error creating batch of suppliers: {e}')

        print('DISK OK')


async def truck_tires_element(suppliers, cities, root):
    print('truck tires elements')
    truck_tires_element = root.find('truckTires')
    if truck_tires_element is not None:
        truck_tire_suppliers_to_create = []
        truck_tire_data_list = []
        truck_tire_objects = {}

        # Collect data about truck tires
        for truck_tire in truck_tires_element.findall('truckTire'):
            truck_tire_data = {
                'id_truck': truck_tire.get('id'),
                'brand_articul': truck_tire.get('brandArticul'),
                'brand': truck_tire.get('brand'),
                'product': truck_tire.get('product'),
                'image': truck_tire.get('image'),
                'full_title': truck_tire.get('fullTitle'),
                'model': truck_tire.get('model'),
                'season': truck_tire.get('season'),
                'indexes': truck_tire.get('indexes'),
                'quadro': truck_tire.get('quadro') == 'да',
                'lightduty': truck_tire.get('lightduty') == 'да',
                'special': truck_tire.get('special') == 'да',
                'width': truck_tire.get('width'),
                'height': truck_tire.get('height'),
                'diameter': truck_tire.get('diameter'),
                'number_of_plies': truck_tire.get('numberOfPlies'),
                'axis': truck_tire.get('axis') or ''
            }

            # Add truck tire data to the list if the full title is present
            if truck_tire_data['full_title']:
                truck_tire_data_list.append(truck_tire_data)

        # After collecting all truck tire data, create truck tire objects in bulk
        truck_tire_objects_created = await bulk_create_truck_tires(truck_tire_data_list)

        # Map created truck tire objects for easy access
        for truck_tire_obj in truck_tire_objects_created:
            if truck_tire_obj:
                truck_tire_objects[truck_tire_obj.full_title] = truck_tire_obj

        # Process suppliers for each truck tire
        for truck_tire in truck_tires_element.findall('truckTire'):
            truck_tire_full_title = truck_tire.get('fullTitle')
            truck_tire_obj = truck_tire_objects.get(truck_tire_full_title)

            for supplier in truck_tire.findall('supplier'):
                articul = supplier.get('articul')
                price = supplier.get('price')
                input_price = supplier.get('inputPrice')
                quantity = supplier.get('quantity')
                supplier_title = supplier.get('supplierTitle')
                city_name = supplier.get('city')
                presence = supplier.get('presence')
                delivery_period_days = supplier.get('deliveryPeriodDays')
                last_availability_date = supplier.get('lastAvailabilityDate')
                sale = supplier.get('sale') == 'yes'

                # Convert date to timezone-aware datetime
                last_availability_date_aware = None
                if last_availability_date:
                    last_availability_date_aware = timezone.make_aware(
                        timezone.datetime.strptime(last_availability_date, '%d.%m.%Y %H:%M:%S')
                    )

                supplier_obj = suppliers.get(supplier_title)
                city_obj = cities.get(city_name)

                if supplier_obj and city_obj and truck_tire_obj:
                    truck_tire_suppliers_to_create.append(
                        TruckTireSupplier(
                            truck_tire=truck_tire_obj,
                            articul=articul,
                            price=price,
                            input_price=input_price,
                            quantity=quantity,
                            supplier=supplier_obj,
                            city=city_obj,
                            presence=presence,
                            delivery_period_days=delivery_period_days,
                            last_availability_date=last_availability_date_aware,
                            sale=sale
                        )
                    )

        # Bulk create all TruckTireSupplier instances at once
        if truck_tire_suppliers_to_create:
            batch_size = 1000  # Adjust batch size as needed
            for i in range(0, len(truck_tire_suppliers_to_create), batch_size):
                batch = truck_tire_suppliers_to_create[i:i + batch_size]
                try:
                    await truck_tire_supplier_bulk_create(batch)
                    print(f'Batch of {len(batch)} suppliers created successfully.')
                except Exception as e:
                    print(f'Error creating batch of suppliers: {e}')

        print('TRUCK TIRES OK')


async def special_tires_element(suppliers, cities, root):
    print('special_tires_element')
    special_tires_element = root.find('specialTires')
    if special_tires_element is not None:
        special_tire_suppliers_to_create = []
        special_tire_data_list = []
        special_tire_objects = {}

        # Collect data about special tires
        for special_tire in special_tires_element.findall('specialTire'):
            special_tire_data = {
                'id_special': special_tire.get('id'),
                'brand_articul': special_tire.get('brandArticul'),
                'brand': special_tire.get('brand'),
                'product': special_tire.get('product'),
                'image': special_tire.get('image'),
                'full_title': special_tire.get('fullTitle'),
                'model': special_tire.get('model'),
                'diameter': special_tire.get('diameter'),
                'typesize': special_tire.get('typesize'),
                'kit': special_tire.get('kit'),
                'indexes': special_tire.get('indexes'),
                'layers': special_tire.get('layers'),
                'camera': special_tire.get('camera'),
                'diagonal': special_tire.get('Dioganal') == 'да',
                'solid': special_tire.get('Solid') == 'да',
                'note': special_tire.get('Note', ''),
                'countries': special_tire.get('Countries', ''),
                'protector_type': special_tire.get('ProtectorType', '')
            }

            # Add special tire data to the list if the full title is present
            if special_tire_data['full_title']:
                special_tire_data_list.append(special_tire_data)

        # After collecting all special tire data, create special tire objects in bulk
        special_tire_objects_created = await bulk_create_special_tires(special_tire_data_list)

        # Map created special tire objects for easy access
        for special_tire_obj in special_tire_objects_created:
            if special_tire_obj:
                special_tire_objects[special_tire_obj.full_title] = special_tire_obj

        # Process suppliers for each special tire
        for special_tire in special_tires_element.findall('specialTire'):
            special_tire_full_title = special_tire.get('fullTitle')
            special_tire_obj = special_tire_objects.get(special_tire_full_title)

            for supplier in special_tire.findall('supplier'):
                articul = supplier.get('articul')
                price = supplier.get('price')
                input_price = supplier.get('inputPrice')
                quantity = supplier.get('quantity')
                supplier_title = supplier.get('supplierTitle')
                city_name = supplier.get('city')
                presence = supplier.get('presence')
                delivery_period_days = supplier.get('deliveryPeriodDays')
                last_availability_date = supplier.get('lastAvailabilityDate')
                sale = supplier.get('sale') == 'yes'

                # Convert date to timezone-aware datetime
                last_availability_date_aware = None
                if last_availability_date:
                    last_availability_date_aware = timezone.make_aware(
                        timezone.datetime.strptime(last_availability_date, '%d.%m.%Y %H:%M:%S')
                    )

                supplier_obj = suppliers.get(supplier_title)
                city_obj = cities.get(city_name)

                if supplier_obj and city_obj and special_tire_obj:
                    special_tire_suppliers_to_create.append(
                        SpecialTireSupplier(
                            special_tire=special_tire_obj,
                            articul=articul,
                            price=price,
                            input_price=input_price,
                            quantity=quantity,
                            supplier=supplier_obj,
                            city=city_obj,
                            presence=presence,
                            delivery_period_days=delivery_period_days,
                            last_availability_date=last_availability_date_aware,
                            sale=sale
                        )
                    )

        # Bulk create all SpecialTireSupplier instances at once
        if special_tire_suppliers_to_create:
            batch_size = 1000  # Adjust batch size as needed
            for i in range(0, len(special_tire_suppliers_to_create), batch_size):
                batch = special_tire_suppliers_to_create[i:i + batch_size]
                try:
                    await special_tire_supplier_bulk_create(batch)
                    print(f'Batch of {len(batch)} suppliers created successfully.')
                except Exception as e:
                    print(f'Error creating batch of suppliers: {e}')

        print('SPECIAL TIRES OK')


async def moto_tires_element(suppliers, cities, root):
    print('moto_tires_element')
    moto_tires_element = root.find('mototires')
    if moto_tires_element is not None:
        moto_tire_suppliers_to_create = []
        moto_tire_data_list = []
        moto_tire_objects = {}

        # Collect data about motorcycle tires
        for moto_tire in moto_tires_element.findall('motoTire'):
            moto_tire_data = {
                'id_moto': moto_tire.get('id'),
                'brand_articul': moto_tire.get('brandArticul'),
                'brand': moto_tire.get('brand'),
                'product': moto_tire.get('product'),
                'image': moto_tire.get('image'),
                'full_title': moto_tire.get('fullTitle'),
                'width': moto_tire.get('width'),
                'height': moto_tire.get('height'),
                'diameter': moto_tire.get('diameter'),
                'indexes': moto_tire.get('indexes'),
                'axis': moto_tire.get('axis'),
                'system': moto_tire.get('system', ''),
                'volume': moto_tire.get('volume'),
                'weight': moto_tire.get('weight'),
                'year': moto_tire.get('year', ''),
                'camera': moto_tire.get('camera'),
                'runflat': moto_tire.get('runflat') == 'да',
                'omolagation': moto_tire.get('omolagation', '')
            }

            # Add motorcycle tire data to the list if the full title is present
            if moto_tire_data['full_title']:
                moto_tire_data_list.append(moto_tire_data)

        # After collecting all motorcycle tire data, create motorcycle tire objects in bulk
        moto_tire_objects_created = await bulk_create_moto_tires(moto_tire_data_list)

        # Map created motorcycle tire objects for easy access
        for moto_tire_obj in moto_tire_objects_created:
            if moto_tire_obj:
                moto_tire_objects[moto_tire_obj.full_title] = moto_tire_obj

        # Process suppliers for each motorcycle tire
        for moto_tire in moto_tires_element.findall('motoTire'):
            moto_tire_full_title = moto_tire.get('fullTitle')
            moto_tire_obj = moto_tire_objects.get(moto_tire_full_title)

            for supplier in moto_tire.findall('supplier'):
                articul = supplier.get('articul')
                price = supplier.get('price')
                input_price = supplier.get('inputPrice')
                quantity = supplier.get('quantity')
                supplier_title = supplier.get('supplierTitle')
                city_name = supplier.get('city')
                presence = supplier.get('presence')
                delivery_period_days = supplier.get('deliveryPeriodDays')
                last_availability_date = supplier.get('lastAvailabilityDate')
                sale = supplier.get('sale') == 'yes'

                # Convert date to timezone-aware datetime
                last_availability_date_aware = None
                if last_availability_date:
                    last_availability_date_aware = timezone.make_aware(
                        timezone.datetime.strptime(last_availability_date, '%d.%m.%Y %H:%M:%S')
                    )

                supplier_obj = suppliers.get(supplier_title)
                city_obj = cities.get(city_name)

                if supplier_obj and city_obj and moto_tire_obj:
                    moto_tire_suppliers_to_create.append(
                        MotoTireSupplier(
                            moto_tire=moto_tire_obj,
                            articul=articul,
                            price=price,
                            input_price=input_price,
                            quantity=quantity,
                            supplier=supplier_obj,
                            city=city_obj,
                            presence=presence,
                            delivery_period_days=delivery_period_days,
                            last_availability_date=last_availability_date_aware,
                            sale=sale
                        )
                    )

        # Bulk create all MotoTireSupplier instances at once
        if moto_tire_suppliers_to_create:
            batch_size = 1000  # Adjust batch size as needed
            for i in range(0, len(moto_tire_suppliers_to_create), batch_size):
                batch = moto_tire_suppliers_to_create[i:i + batch_size]
                try:
                    await moto_tire_supplier_bulk_create(batch)
                    print(f'Batch of {len(batch)} suppliers created successfully.')
                except Exception as e:
                    print(f'Error creating batch of suppliers: {e}')

        print('MOTO TIRES OK')

