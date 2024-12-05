import asyncio
import math
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Type

from asgiref.sync import sync_to_async
from django.db import transaction
from django.db.models import Max
import numpy
import pandas as pd
import openpyxl

from itertools import groupby

from apps.company.models import Company
from apps.company.utils.functions import get_measurement
from apps.company.utils.general_tools import format_number
from apps.services.models import NoPriceRoznProduct
from apps.suppliers.models import Tire, TireSupplier, Supplier, CompanySupplier, TruckTireSupplier, DiskSupplier, \
    SpecialTireSupplier, MotoTireSupplier, TruckDiskSupplier

headers = [
    'id', 'brandArticul', 'brand', 'product', 'image', 'fullTitle', 'headline',
    'measurement', 'recommendedPrice', 'model', 'width', 'height', 'diameter',
    'season', 'spike', 'lightduty', 'indexes', 'system', 'omolagation', 'mud',
    'at', 'runFlatTitle', 'fr', 'xl', 'autobrand', 'pcd', 'boltcount', 'drill',
    'outfit', 'dia', 'color', 'type', 'numberOfPlies', 'axis', 'quadro',
    'special', 'note', 'typesize', 'kit', 'layers', 'camera', 'Dioganal',
    'Solid', 'Note', 'Countries', 'runflat', 'ProtectorType', 'supplier-articul',
    'supplier-supplierTitle', 'supplier-quantity', 'supplier-price',
    'supplier-inputPrice', 'supplier-price_rozn', 'supplier-deliveryPeriodDays',
    'supplier-tireType', 'supplier-stock', 'supplier-supplier',
    'supplier-presence', 'supplier-lastAvailabilityDate', 'supplier-sale',
    'supplier-year', 'supplier-description'
]


def get_available_products_for_company(company_id, types, availability, format, new_price_no_rozn):
    # Получаем всех поставщиков, связанных с данной компанией через CompanySupplier
    suppliers = Supplier.objects.filter(companysupplier__company_id=company_id)

    # Инициализируем словарь для группировки доступных продуктов
    grouped_products = {
        'tires': {},
        'disks': {},
        'truck_tires': {},
        'special_tires': {},
        'moto_tires': {},
        'truck_disks': {},
    }
    # Проверяем, какие типы продуктов были выбраны
    if 'tires' in types:
        tire_filters = {
            'supplier__in': suppliers,
        }
        if availability == 'in_stock':
            tire_filters['delivery_period_days'] = 0
        elif availability == 'out_of_stock':
            tire_filters['delivery_period_days__gte'] = 1

        available_tires = TireSupplier.objects.filter(**tire_filters).select_related('tire')

        for tire_supplier in available_tires:
            tire_id = tire_supplier.tire.id_tire
            if tire_id not in grouped_products['tires']:
                grouped_products['tires'][tire_id] = {
                    'product': tire_supplier.tire,
                    'suppliers': []
                }
            grouped_products['tires'][tire_id]['suppliers'].append(tire_supplier)

    if 'disks' in types:
        # Получаем все диски, которые в наличии у этих поставщиков
        disk_filters = {
            'supplier__in': suppliers,
        }
        if availability == 'in_stock':
            disk_filters['delivery_period_days'] = 0
        elif availability == 'out_of_stock':
            disk_filters['delivery_period_days__gte'] = 1

        available_disks = DiskSupplier.objects.filter(**disk_filters).select_related('disk')

        for disk_supplier in available_disks:
            disk_id = disk_supplier.disk.id_disk  # Предполагается, что у модели Disk есть поле id_disk
            if disk_id not in grouped_products['disks']:
                grouped_products['disks'][disk_id] = {
                    'product': disk_supplier.disk,
                    'suppliers': []
                }
            grouped_products['disks'][disk_id]['suppliers'].append(disk_supplier)

    if 'truck_tires' in types:
        # Получаем все грузовые шины, которые в наличии у этих поставщиков
        truck_tire_filters = {
            'supplier__in': suppliers,
        }
        if availability == 'in_stock':
            truck_tire_filters['delivery_period_days'] = 0
        elif availability == 'out_of_stock':
            truck_tire_filters['delivery_period_days__gte'] = 1

        available_truck_tires = TruckTireSupplier.objects.filter(**truck_tire_filters).select_related('truck_tire')

        for truck_tire_supplier in available_truck_tires:
            truck_tire_id = truck_tire_supplier.truck_tire.id_truck
            if truck_tire_id not in grouped_products['truck_tires']:
                grouped_products['truck_tires'][truck_tire_id] = {
                    'product': truck_tire_supplier.truck_tire,
                    'suppliers': []
                }
            grouped_products['truck_tires'][truck_tire_id]['suppliers'].append(truck_tire_supplier)

    if 'special_tires' in types:
        # Получаем все специальные шины, которые в наличии у этих поставщиков
        special_tire_filters = {
            'supplier__in': suppliers,
        }
        if availability == 'in_stock':
            special_tire_filters['delivery_period_days'] = 0
        elif availability == 'out_of_stock':
            special_tire_filters['delivery_period_days__gte'] = 1

        available_special_tires = SpecialTireSupplier.objects.filter(**special_tire_filters).select_related(
            'special_tire')

        for special_tire_supplier in available_special_tires:
            special_tire_id = special_tire_supplier.special_tire.id_special  # Предполагается, что у модели SpecialTire есть поле id_special_tire
            if special_tire_id not in grouped_products['special_tires']:
                grouped_products['special_tires'][special_tire_id] = {
                    'product': special_tire_supplier.special_tire,
                    'suppliers': []
                }
            grouped_products['special_tires'][special_tire_id]['suppliers'].append(special_tire_supplier)

    if 'moto_tires' in types:
        # Получаем все мотоциклетные шины, которые в наличии у этих поставщиков
        moto_tire_filters = {
            'supplier__in': suppliers,
        }
        if availability == 'in_stock':
            moto_tire_filters['delivery_period_days'] = 0
        elif availability == 'out_of_stock':
            moto_tire_filters['delivery_period_days__gte'] = 1

        available_moto_tires = MotoTireSupplier.objects.filter(**moto_tire_filters).select_related('moto_tire')

        for moto_tire_supplier in available_moto_tires:
            moto_tire_id = moto_tire_supplier.moto_tire.id_moto  # Предполагается, что у модели MotoTire есть поле id_moto_tire
            if moto_tire_id not in grouped_products['moto_tires']:
                grouped_products['moto_tires'][moto_tire_id] = {
                    'product': moto_tire_supplier.moto_tire,
                    'suppliers': []
                }
            grouped_products['moto_tires'][moto_tire_id]['suppliers'].append(moto_tire_supplier)
    if 'truck_disks' in types:
        truck_disk_filters = {
            'supplier__in': suppliers,
        }
        if availability == 'in_stock':
            truck_disk_filters['delivery_period_days'] = 0
        elif availability == 'out_of_stock':
            truck_disk_filters['delivery_period_days__gte'] = 1

        available_truck_disk = TruckDiskSupplier.objects.filter(**truck_disk_filters).select_related('truck_disk')

        for truck_disk_supplier in available_truck_disk:
            truck_disk_id = truck_disk_supplier.truck_disk.id_disk
            if truck_disk_id not in grouped_products['truck_disks']:
                grouped_products['truck_disks'][truck_disk_id] = {
                    'product': truck_disk_supplier.truck_disk,
                    'suppliers': []
                }
            grouped_products['truck_disks'][truck_disk_id]['suppliers'].append(truck_disk_supplier)
    # Сохраняем данные в XML файл
    save_tires_to_xml_availability(grouped_products, company_id, types, format, new_price_no_rozn)
    return grouped_products


from datetime import datetime, timezone


def save_tires_to_xml_availability(grouped_products, company_id, types, format, new_price_no_rozn):
    # Создаем корневой элемент
    # Получаем текущее время в UTC
    current_date = datetime.now(timezone.utc)

    # Форматируем дату в нужный формат
    formatted_date = current_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    root = ET.Element("root", date=formatted_date)
    # Обрабатываем шины
    if 'tires' in types:
        if len(grouped_products['tires']) != 0:
            process_tires(root, grouped_products['tires'], company_id, new_price_no_rozn)

    if 'disks' in types:
        if len(grouped_products['disks']) != 0:
            process_disks(root, grouped_products['disks'], company_id, new_price_no_rozn)

    if 'truck_disks' in types:
        if len(grouped_products['truck_disks']) != 0:
            process_truck_disks(root, grouped_products['truck_disks'], company_id, new_price_no_rozn)

    if 'moto_tires' in types:
        if len(grouped_products['moto_tires']) != 0:
            process_moto(root, grouped_products['moto_tires'], company_id, new_price_no_rozn)

    if 'special_tires' in types:
        if len(grouped_products['special_tires']) != 0:
            process_special_tires(root, grouped_products['special_tires'], company_id, new_price_no_rozn)

    # Обрабатываем грузовые шины
    if 'truck_tires' in types:
        if len(grouped_products['truck_tires']) != 0:
            process_truck_tires(root, grouped_products['truck_tires'], company_id, new_price_no_rozn)

    # Генерируем строку XML
    xml_str = ET.tostring(root, encoding='utf-8').decode('utf-8')
    xml = ET.fromstring(xml_str)
    date = datetime.now().strftime("%d-%m-%H-%M")
    if format == 'xlsx':

        xml_element = ET.fromstring(xml_str)
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(headers)
        items = [xml.find('tires'),
                 xml.find('disks'),
                 xml.find('truckTires'),
                 xml.find('truckDisks'),
                 xml.find('specialTires'),
                 xml.find('motoTires'),
                 ]
        find_item = ['tire', 'disk', 'truckTire', 'truckDisk', 'specialTire', 'motoTire']
        for index in range(len(items)):
            if items[index]:
                for record in items[index].findall(find_item[index]):
                    supplier = record.find('supplier')
                    row_data = [
                        record.get('id', ''),
                        record.get('brandArticul', ''),
                        record.get('brand', ''),
                        record.get('product', ''),
                        record.get('image', ''),
                        record.get('fullTitle', ''),
                        record.get('headline', ''),
                        record.get('measurement', ''),
                        record.get('recommendedPrice', ''),
                        record.get('model', ''),
                        record.get('width', ''),
                        record.get('height', ''),
                        record.get('diameter', ''),
                        record.get('season', ''),
                        record.get('spike', ''),
                        record.get('lightduty', ''),
                        record.get('indexes', ''),
                        record.get('system', ''),
                        record.get('omolagation', ''),
                        record.get('mud', ''),
                        record.get('at', ''),
                        record.get('runFlatTitle', ''),
                        record.get('fr', ''),
                        record.get('xl', ''),
                        record.get('autobrand', ''),
                        record.get('pcd', ''),
                        record.get('boltcount', ''),
                        record.get('drill', ''),
                        record.get('outfit', ''),
                        record.get('dia', ''),
                        record.get('color', ''),
                        record.get('type', ''),
                        record.get('numberOfPlies', ''),
                        record.get('axis', ''),
                        record.get('quadro', ''),
                        record.get('special', ''),
                        record.get('note', ''),
                        record.get('typesize', ''),
                        record.get('kit', ''),
                        record.get('layers', ''),
                        record.get('camera', ''),
                        record.get('Dioganal', ''),
                        record.get('Solid', ''),
                        record.get('Note', ''),
                        record.get('Countries', ''),
                        record.get('runflat', ''),
                        record.get('ProtectorType', ''),
                        supplier.get('articul', '') if supplier is not None else '',
                        supplier.get('supplierTitle', '') if supplier is not None else '',
                        supplier.get('quantity', '') if supplier is not None else '',
                        supplier.get('price', '') if supplier is not None else '',
                        supplier.get('inputPrice', '') if supplier is not None else '',
                        supplier.get('price_rozn', '') if supplier is not None else '',
                        supplier.get('deliveryPeriodDays', '') if supplier is not None else '',
                        supplier.get('tireType', '') if supplier is not None else '',
                        supplier.get('stock', '') if supplier is not None else '',
                        supplier.get('supplier', '') if supplier is not None else '',
                        supplier.get('presence', '') if supplier is not None else '',
                        supplier.get('lastAvailabilityDate', '') if supplier is not None else '',
                        supplier.get('sale', '') if supplier is not None else '',
                        supplier.get('year', '') if supplier is not None else '',
                        supplier.get('description', '') if supplier is not None else ''
                    ]
                    ws.append(row_data)
        # Сохранение в файл
        name = f'Обработчик-{date}.xlsx'
        wb.save(f'media/uploads/{company_id}/{name}')

    else:
        name = f'Обработчик-{date}.xml'

        # Сохраняем XML в файл
        with open(f'media/uploads/{company_id}/{name}', 'a', encoding='utf-8') as xml_file:
            xml_file.write(xml_str.replace("><", ">\n<"))  # Добавляем переносы строк между элементами

        print(f"XML сохранен в файл: {name}")


def get_headline(result, category) -> str:
    result = result['product']
    diameter, width = None, None
    try:
        if result.diameter:
            diameter = numpy.float16(result.diameter.replace(',', '.'))
        try:
            width = numpy.float16(result.width.replace(',', '.'))
        except:
            width = 'Full'
        try:
            height = numpy.float16(result.height.replace(',', '.'))
        except:
            height = 'Full'
    except ValueError as e:
        print(f"Error converting tire size: {e}")
        return ""  # Return an empty string or handle the error as needed
    diameter_str = format_number(diameter)
    height_str = format_number(height) if height != 'Full' else 'Full'
    width_str = format_number(width) if width != 'Full' else 'Full'

    res = ""
    if category == "tires" or category == "truckTires" or category == "mototires":
        res += result.brand + " "
        res += result.product + " "
        product_width_res = width_str
        product_height_res = height_str
        if product_width_res != "":
            res += product_width_res + " "
        if product_height_res != "":
            res += product_height_res
        return res.strip()
    elif category == "specialTires":
        res += result.brand + " "
        res += result.product + " "
        res += result.typesize
        return res.strip()
    elif category == "disks":
        if result.brand != "":
            res += result.brand + " "
        if result.product != "":
            res += result.product + " "
        if result.width != "":
            res += width_str + ' '
        if result.diameter != "":
            res += diameter_str + " "
        if result.outfit != "":
            res += result.outfit.replace(",", ".").strip("0").strip(".") + " "
        if result.boltcount != "":
            res += result.boltcount.replace(",", ".").strip("0").strip(".") + " "
        if result.pcd != "":
            res += result.pcd.replace(",", ".").strip("0").strip(".") + " "
        if result.dia != "":
            res += diameter_str + " "
        if result.color != "":
            res += result.color + " "
        return res.strip()
    return res


def process_tires(root, tires, company_id, new_price_no_rozn):
    tires_elements = ET.SubElement(root, 'tires')

    for tire_id, data in tires.items():
        tire_element = ET.SubElement(tires_elements, "tire",
                                     id=tire_id,
                                     brandArticul=str(data['product'].brand_article) if data[
                                         'product'].brand_article else '',
                                     brand=data['product'].brand,
                                     product=data['product'].product,
                                     fullTitle=data['product'].full_title,
                                     headline=get_headline(data, 'tires'),  # TODO
                                     measurement=get_measurement(data['product'].width),
                                     recommendedPrice='',
                                     model=data['product'].model,
                                     width=data['product'].width,
                                     height=data['product'].height,
                                     diameter=data['product'].diameter,
                                     season=data['product'].season,
                                     spike="да" if data['product'].spike else "нет",
                                     lightduty="да" if data['product'].lightduty else "нет",
                                     indexes=str(data['product'].indexes) if data['product'].indexes else '',
                                     system='',
                                     omolagation=str(data['product'].omolagation) if data[
                                         'product'].omolagation else '',
                                     mud=str(data['product'].mud) if data['product'].mud else '',
                                     at=str(data['product'].at) if data['product'].at else '',
                                     runFlatTitle=str(data['product'].runflat) if data['product'].runflat else '',
                                     fr=str(data['product'].fr) if data['product'].fr else '',
                                     xl=str(data['product'].xl) if data['product'].xl else '',
                                     autobrand="",
                                     pcd="",
                                     boltcount="",
                                     drill="",
                                     outfit="",
                                     dia="",
                                     color="",
                                     type="",
                                     numberOfPlies="",
                                     axis="",
                                     quadro="",
                                     special="",
                                     note="",
                                     typesize="",
                                     kit="",
                                     layers="",
                                     camera="",
                                     Dioganal="",
                                     Solid="",
                                     Note="",
                                     Countries="",
                                     runflat="да" if data['product'].runflat else "нет",
                                     ProtectorType=""
                                     )

        # Sort suppliers and process them
        sorted_suppliers = sort_suppliers(data['suppliers'], company_id)
        articuls, best_supplier, best_price, total_quantity, best_delivery_period_days, product_supplier, max_price_rozn = process_suppliers(
            sorted_suppliers, data['product'], company_id)

        if best_supplier:
            create_supplier_element(tire_element, articuls, best_supplier, best_price, total_quantity,
                                    best_delivery_period_days, product_supplier=product_supplier, company_id=company_id,
                                    new_price_no_rozn=new_price_no_rozn, data=data, max_price_rozn=max_price_rozn)


def get_drill(result) -> str:
    if result.boltcount != "" and result.pcd != "":
        product_boltcount_res = result.boltcount.replace(",", ".").strip("0").strip(".")
        product_pcd_res = result.pcd.replace(",", ".").strip("0").strip(".")
        if product_boltcount_res == "" and product_pcd_res == "":
            return ""
        return f"{product_boltcount_res}x{product_pcd_res}"
    return ""


def process_disks(root, disks, company_id, new_price_no_rozn):
    disks_elements = ET.SubElement(root, 'disks')
    for disk_id, data in disks.items():
        disk_element = ET.SubElement(disks_elements, "disk",
                                     id=disk_id,
                                     brandArticul=str(data['product'].brand_articul) if data[
                                         'product'].brand_articul else '',
                                     brand=data['product'].brand,
                                     product=data['product'].product,
                                     fullTitle=data['product'].full_title,
                                     headline=get_headline(data, 'disks'),
                                     # measurement=get_measurement(data['product'].width),
                                     measurement="",
                                     recommendedPrice='',
                                     model=data['product'].model,
                                     width=(data['product'].width).replace(',', '.'),
                                     height='',
                                     diameter="{:.2f}".format(float(data['product'].diameter)),
                                     season='',
                                     spike='',
                                     lightduty="",
                                     indexes='',
                                     system='',
                                     omolagation='',
                                     mud='',
                                     at='',
                                     runFlatTitle='',
                                     fr='',
                                     xl='',
                                     autobrand='',
                                     pcd="{:.2f}".format(float((data['product'].pcd).replace(',', '.'))),
                                     boltcount=str(data['product'].boltcount) if data['product'].boltcount else '',
                                     drill=get_drill(data['product']),
                                     outfit="{:.2f}".format(float((data['product'].outfit).replace(',', '.'))) if data[
                                         'product'].outfit else '',
                                     dia="{:.2f}".format(float((data['product'].dia).replace(',', '.'))) if data[
                                         'product'].dia else '',
                                     color=data['product'].color,
                                     type=data['product'].type,
                                     numberOfPlies='',
                                     axis='',
                                     quadro='',
                                     special='',
                                     note='',
                                     typesize='',
                                     kit='',
                                     layers='',
                                     camera='',
                                     Dioganal='',
                                     Solid='',
                                     Note='',
                                     Countries='',
                                     runflat="",
                                     ProtectorType=''
                                     )

        sorted_suppliers = sort_suppliers(data['suppliers'], company_id)

        articuls, best_supplier, best_price, total_quantity, best_delivery_period_days, product_supplier, max_price_rozn = process_suppliers(
            sorted_suppliers, data['product'], company_id, is_disk=True)

        if best_supplier:
            create_supplier_element(disk_element, articuls, best_supplier, best_price, total_quantity,
                                    best_delivery_period_days, product_supplier=product_supplier, company_id=company_id,
                                    is_disk=True,new_price_no_rozn=new_price_no_rozn, max_price_rozn=max_price_rozn)


def process_truck_tires(root, truck_tires, company_id, new_price_no_rozn):
    trucks = ET.SubElement(root, 'trucks')

    for truck_tire_id, data in truck_tires.items():
        # Create the truck tire element with default values for optional fields
        truck_tire_element = ET.SubElement(trucks, "truckTire",
                                           id=truck_tire_id,
                                           brandArticul=str(data['product'].brand_articul) if data[
                                               'product'].brand_articul else '',
                                           brand=data['product'].brand or '',
                                           product=data['product'].product or '',
                                           fullTitle=data['product'].full_title or '',
                                           headline=get_headline(data, 'truckTires'),
                                           measurement=get_measurement(data['product'].width) or '',
                                           recommendedPrice='',
                                           model=data['product'].model or '',
                                           width=data['product'].width or '',
                                           height=data['product'].height or '',
                                           diameter=data['product'].diameter or '',
                                           season=data['product'].season or '',
                                           spike='',
                                           lightduty="да" if data['product'].lightduty else "нет",
                                           indexes=str(data['product'].indexes) if data['product'].indexes else '',
                                           system='',
                                           omolagation='',
                                           mud='',
                                           at='',
                                           runFlatTitle='',
                                           fr='',
                                           xl='',
                                           autobrand='',
                                           pcd='',
                                           boltcount='',
                                           drill='',
                                           outfit='',
                                           dia='',
                                           color='',
                                           type='',
                                           numberOfPlies=str(data['product'].number_of_plies) if data[
                                               'product'].number_of_plies else '',
                                           axis=str(data['product'].axis) if data['product'].axis else '',
                                           quadro=str(data['product'].quadro) if data['product'].quadro else '',
                                           special=str(data['product'].special) if data['product'].special else '',
                                           note='',
                                           typesize='',
                                           kit='',
                                           layers='',
                                           camera='',
                                           Dioganal='',
                                           Solid='',
                                           Note='',
                                           Countries='',
                                           runflat='',
                                           ProtectorType='',
                                           )

        # Sort suppliers and process them
        sorted_suppliers = sort_suppliers(data['suppliers'], company_id)

        articuls, best_supplier, best_price, total_quantity, best_delivery_period_days, product_supplier, max_price_rozn = process_suppliers(
            sorted_suppliers, data['product'], company_id, is_truck_tire=True)
        # Create supplier element if a best supplier is found
        if best_supplier:
            create_supplier_element(truck_tire_element, articuls, best_supplier, best_price, total_quantity,
                                    best_delivery_period_days, product_supplier=product_supplier, company_id=company_id,
                                    is_truck_tire=True, new_price_no_rozn=new_price_no_rozn, max_price_rozn=max_price_rozn)


def process_truck_disks(root, truck_disks, company_id, new_price_no_rozn):
    trucks = ET.SubElement(root, 'truckDisks')
    for truck_disk_id, data in truck_disks.items():
        truck_disk_element = ET.SubElement(trucks, "truckDisk",
                                           id=truck_disk_id,
                                           brandArticul=str(data['product'].brand_articul) if data[
                                               'product'].brand_articul else '',
                                           brand=data['product'].brand,
                                           product=data['product'].product,
                                           fullTitle=data['product'].full_title,
                                           headline=get_headline(data, 'disks'),
                                           measurement=get_measurement(data['product'].width),
                                           recommendedPrice='',
                                           model=data['product'].model,
                                           width=data['product'].width,
                                           height='',
                                           diameter=data['product'].diameter,
                                           season='',
                                           spike="",
                                           lightduty='',
                                           indexes='',
                                           system='',
                                           omolagation='',
                                           mud='',
                                           at='',
                                           runFlatTitle='',
                                           fr='',
                                           xl='',
                                           autobrand='',
                                           pcd=str(data['product'].pcd if data['product'].pcd else ''),
                                           boltcount=str(
                                               data['product'].boltcount if data['product'].boltcount else ''),
                                           drill='',
                                           outfit='',
                                           dia=str(data['product'].dia if data['product'].dia else ''),
                                           color=str(data['product'].color if data['product'].color else ''),
                                           type=str(data['product'].type if data['product'].type else ''),
                                           numberOfPlies='',
                                           axis='',
                                           quadro='',
                                           special='',
                                           note='',
                                           typesize='',
                                           kit='',
                                           layers='',
                                           camera='',
                                           Dioganal='',
                                           Solid='',
                                           Note=str(data['product'].note) if data[
                                               'product'].note else '',
                                           Countries='',
                                           runflat='',
                                           ProtectorType='',
                                           )

        sorted_suppliers = sort_suppliers(data['suppliers'], company_id)

        articuls, best_supplier, best_price, total_quantity, best_delivery_period_days, product_supplier, max_price_rozn = process_suppliers(
            sorted_suppliers, data['product'], company_id, is_truck_disks=True)

        if best_supplier:
            create_supplier_element(truck_disk_element, articuls, best_supplier, best_price, total_quantity,
                                    best_delivery_period_days, product_supplier=product_supplier, company_id=company_id,
                                    is_truck_disk=True, new_price_no_rozn=new_price_no_rozn, max_price_rozn=max_price_rozn)


def process_moto(root, moto, company_id, new_price_no_rozn):
    moto_root = ET.SubElement(root, 'mototires')
    for moto_id, data in moto.items():
        moto_element = ET.SubElement(moto_root, "motoTire",
                                     id=moto_id,
                                     brandArticul=str(data['product'].brand_articul) if data[
                                         'product'].brand_articul else '',
                                     brand=data['product'].brand,
                                     product=data['product'].product,
                                     fullTitle=data['product'].full_title,
                                     headline=get_headline(data, 'mototires'),
                                     measurement=str(data['product'].width) if data[
                                         'product'].width else '',
                                     recommendedPrice='',
                                     model='',
                                     width=data['product'].width,
                                     height=str(data['product'].height) if data[
                                         'product'].height else '',
                                     diameter=data['product'].diameter,
                                     season='',
                                     spike="",
                                     lightduty='',
                                     indexes='',
                                     system='',
                                     omolagation=str(data['product'].omolagation) if data[
                                         'product'].omolagation else '',
                                     mud='',
                                     at='',
                                     fr='',
                                     xl='',
                                     autobrand='',
                                     pcd='',
                                     boltcount='',
                                     drill='',
                                     outfit='',
                                     dia='',
                                     color='',
                                     type='',
                                     numberOfPlies='',
                                     axis=str(data['product'].axis) if data[
                                         'product'].axis else '',
                                     quadro='',
                                     special='',
                                     note='',
                                     typesize='',
                                     kit='',
                                     layers='',
                                     camera=str(data['product'].camera) if data[
                                         'product'].camera else '',
                                     Dioganal='',
                                     Solid='',
                                     Note='',
                                     Countries='',
                                     runflat=str(data['product'].runflat) if data[
                                         'product'].runflat else '',
                                     ProtectorType='',
                                     )

        sorted_suppliers = sort_suppliers(data['suppliers'], company_id)

        articuls, best_supplier, best_price, total_quantity, best_delivery_period_days, product_supplier, max_price_rozn = process_suppliers(
            sorted_suppliers, data['product'], company_id, moto=True)

        if best_supplier:
            create_supplier_element(moto_element, articuls, best_supplier, best_price, total_quantity,
                                    best_delivery_period_days, product_supplier=product_supplier, company_id=company_id,
                                    moto=True, new_price_no_rozn=new_price_no_rozn, max_price_rozn=max_price_rozn)


def sort_suppliers(suppliers, company_id):
    def get_supplier_info(supplier):
        try:
            company_supplier = CompanySupplier.objects.get(company_id=company_id, supplier=supplier.supplier)
            price = supplier.price.strip().replace(',', '.')  # Remove any leading/trailing whitespace
            price_value = float(price) if price else float('inf')  # Use float('inf') if price is empty

            return (
                -company_supplier.priority if company_supplier.priority is not None else float('inf'),
                company_supplier.visual_priority if company_supplier.visual_priority is not None else float('inf'),
                supplier.quantity,
                price_value  # Now safely converted to float
            )
        except CompanySupplier.DoesNotExist:
            return (float('inf'), float('inf'), supplier.quantity, float('inf'))  # Default to inf for missing suppliers

    return sorted(suppliers, key=get_supplier_info, reverse=True)


def process_suppliers(sorted_suppliers, product, company_id, is_disk=False,
                      is_truck_tire=False, is_truck_disks=False, moto=False,
                      special=False):
    articuls = []
    best_supplier = None
    best_price = None
    total_quantity = 0
    best_delivery_period_days = None
    product_supplier = None  # Initialize product_supplier
    max_price_rozn = None
    for supplier in sorted_suppliers:
        company_supplier = CompanySupplier.objects.get(company_id=company_id, supplier=supplier.supplier)
        articuls.append(company_supplier.article_number or '')

        if is_disk:
            product_supplier = DiskSupplier.objects.filter(disk=product, supplier=supplier.supplier).first()
            max_price_rozn = DiskSupplier.objects.filter(disk__full_title=product_supplier.disk.full_title).aggregate(
                Max('price_rozn'))
        elif is_truck_tire:
            product_supplier = TruckTireSupplier.objects.filter(truck_tire=product, supplier=supplier.supplier).first()
            max_price_rozn = TruckTireSupplier.objects.filter(truck_tire__full_title=product_supplier.truck_tire.full_title).aggregate(
                Max('price_rozn'))
        elif is_truck_disks:
            product_supplier = TruckDiskSupplier.objects.filter(truck_disk=product, supplier=supplier.supplier).first()
            max_price_rozn = TruckDiskSupplier.objects.filter(truck_disk__full_title=product_supplier.truck_disk.full_title).aggregate(
                Max('price_rozn'))
        elif special:
            product_supplier = SpecialTireSupplier.objects.filter(special_tire=product,
                                                                  supplier=supplier.supplier).first()
            max_price_rozn = SpecialTireSupplier.objects.filter(special_tire__full_title=product_supplier.special_tire.full_title).aggregate(
                Max('price_rozn'))
        elif moto:
            product_supplier = MotoTireSupplier.objects.filter(moto_tire=product, supplier=supplier.supplier).first()
            max_price_rozn = MotoTireSupplier.objects.filter(moto_tire__full_title=product_supplier.moto_tire.full_title).aggregate(
                Max('price_rozn'))
        else:
            product_supplier = TireSupplier.objects.filter(tire=product, supplier=supplier.supplier).first()
            max_price_rozn = TireSupplier.objects.filter(tire__full_title=product_supplier.tire.full_title).aggregate(
                Max('price_rozn'))

        if product_supplier:
            total_quantity += int(product_supplier.quantity)

            if best_supplier is None:
                best_supplier = company_supplier
                best_price = product_supplier.price
                best_delivery_period_days = product_supplier.delivery_period_days
            else:
                # Ensure that both priorities are not None before comparison
                company_priority = company_supplier.priority if company_supplier.priority is not None else float('inf')
                best_priority = best_supplier.priority if best_supplier.priority is not None else float('inf')

                is_better_priority = company_priority < best_priority

                # Check if both visual priorities are not None before comparison
                if company_priority == best_priority:
                    company_visual_priority = company_supplier.visual_priority if company_supplier.visual_priority is not None else float(
                        'inf')
                    best_visual_priority = best_supplier.visual_priority if best_supplier.visual_priority is not None else float(
                        'inf')
                    is_same_priority_but_better_visual = company_visual_priority < best_visual_priority
                else:
                    is_same_priority_but_better_visual = False

                # Update best supplier if the current company has a better priority or visual priority
                if is_better_priority or is_same_priority_but_better_visual:
                    best_supplier = company_supplier
                    best_price = product_supplier.price

            # Update the best delivery period days to the maximum delivery period
            if product_supplier.delivery_period_days is not None:
                if best_delivery_period_days is None or product_supplier.delivery_period_days > best_delivery_period_days:
                    best_delivery_period_days = product_supplier.delivery_period_days

    return (articuls, best_supplier, best_price, total_quantity, best_delivery_period_days, product_supplier,
            max_price_rozn['price_rozn__max'])


def process_special_tires(root, special_tires, company_id, new_price_no_rozn):
    special_root = ET.SubElement(root, 'specialTires')
    for special_tire_id, data in special_tires.items():
        special_tire_element = ET.SubElement(special_root, "specialTire",
                                             id=special_tire_id,
                                             brandArticul=str(data['product'].brand_articul) if data[
                                                 'product'].brand_articul else '',
                                             brand=data['product'].brand,
                                             product=data['product'].product,
                                             fullTitle=data['product'].full_title,
                                             headline=get_headline(data, 'SpecialTires'),
                                             measurement='',
                                             recommendedPrice='',
                                             model=data['product'].model,
                                             width='',
                                             height='',
                                             diameter=data['product'].diameter,
                                             season='',
                                             spike="",
                                             lightduty='',
                                             indexes=str(data['product'].indexes) if data['product'].indexes else '',
                                             system='',
                                             omolagation='',
                                             mud='',
                                             at='',
                                             runFlatTitle='',
                                             fr='',
                                             xl='',
                                             autobrand='',
                                             pcd='',
                                             boltcount='',
                                             drill='',
                                             outfit='',
                                             dia='',
                                             color='',
                                             type='',
                                             numberOfPlies='',
                                             axis='',
                                             quadro='',
                                             special='',
                                             note=str(data['product'].note) if data[
                                                 'product'].note else '',
                                             typesize=str(data['product'].typesize) if data[
                                                 'product'].typesize else '',
                                             kit=str(data['product'].kit) if data[
                                                 'product'].kit else '',
                                             layers=str(data['product'].layers) if data[
                                                 'product'].layers else '',
                                             camera=str(data['product'].camera) if data[
                                                 'product'].camera else '',
                                             Dioganal=str(data['product'].diagonal) if data[
                                                 'product'].diagonal else '',
                                             Solid=str(data['product'].solid) if data[
                                                 'product'].solid else '',
                                             Note=str(data['product'].note) if data[
                                                 'product'].note else '',
                                             Countries=str(data['product'].countries) if data[
                                                 'product'].countries else '',
                                             runflat='',
                                             ProtectorType=str(data['product'].protector_type) if data[
                                                 'product'].protector_type else '',
                                             )

        sorted_suppliers = sort_suppliers(data['suppliers'], company_id)

        articuls, best_supplier, best_price, total_quantity, best_delivery_period_days, product_supplier, max_price_rozn = process_suppliers(
            sorted_suppliers, data['product'], company_id, special=True)

        if best_supplier:
            create_supplier_element(special_tire_element, articuls, best_supplier, best_price, total_quantity,
                                    best_delivery_period_days, product_supplier=product_supplier, company_id=company_id,
                                    special=True, new_price_no_rozn=new_price_no_rozn, max_price_rozn=max_price_rozn)


def price_rozn(price: str, company_id, best_price, new_price_no_rozn, product_supplier, best_supplier, data, parent_element):
    if price:
        price = float(price.replace(',', '.'))
        price_multiplier = Company.objects.get(id=company_id).price_multiplier
        try:
            brand = data['product'].brand
        except:
            brand = None
        try:
            product=data['product'].product
        except:
            product = None
        new_product = NoPriceRoznProduct.objects.create(
            id_product=product_supplier.articul,
            brand=brand,
            product=product,
            supplier=best_supplier.supplier.name
        )
        new_price_no_rozn.products.add(new_product)
        return str(price_rozn_pow(price * price_multiplier))  # TODO проверить с нулем
    return str(price_rozn_pow(best_price))


def price_rozn_pow(price_rozn):
    price_rozn = str(price_rozn).replace(',', '.')
    if price_rozn:
        return math.ceil(float(price_rozn))
    return ''


def create_supplier_element(parent_element, articuls, best_supplier, best_price, total_quantity,
                            best_delivery_period_days, company_id, product_supplier=None, is_disk=False,
                            is_truck_tire=False, is_truck_disk=False,
                            moto=False, special=False, new_price_no_rozn=None, data=None, max_price_rozn=None):
    presence_status = 'В наличии' if int(best_delivery_period_days) == 0 else 'Под заказ'
    stock = 'Наличие' if int(best_delivery_period_days) == 0 else 'Под заказ'
    tire_type = None
    if moto:
        tire_type = 'Мотошины'
    elif is_truck_tire:
        tire_type = 'Грузовая и LT'
    elif is_truck_disk:
        tire_type = 'Грузовые диски'
    elif is_disk:
        tire_type = 'Диск'
    elif special:
        tire_type = 'Специальные'
    else:
        tire_type = 'Обычная'

    sale = 'yes'
    if product_supplier.sale == 'False':
        sale = 'no'
    supplier_element = ET.SubElement(parent_element, "supplier",
                                     articul=", ".join([el for el, _ in groupby(articuls)]),
                                     supplierTitle=articuls[0],
                                     quantity=str(total_quantity),
                                     price=str(price_rozn_pow(best_price.replace(',', '.'))),
                                     inputPrice=str(price_rozn_pow(product_supplier.input_price)) if product_supplier
                                     else '',
                                     price_rozn=str(price_rozn_pow(max_price_rozn)) if
                                     max_price_rozn else price_rozn(
                                         product_supplier.input_price, company_id, best_price, new_price_no_rozn,
                                         product_supplier, best_supplier, data, parent_element),
                                     deliveryPeriodDays=str(
                                         best_delivery_period_days) if best_delivery_period_days is not None else '',
                                     tireType=tire_type,
                                     stock=stock,
                                     supplier=str(best_supplier.supplier.id),
                                     presence=presence_status,
                                     lastAvailabilityDate=product_supplier.last_availability_date.strftime(
                                         "%d.%m.%Y %H:%M:%S") if product_supplier else '',
                                     sale=sale,
                                     year=""
                                     )


# @sync_to_async
# def get_max_prices(supplier_model, product_field):
#     try:
#         return (
#             supplier_model.objects
#             .values(f"{product_field}__full_title")  # Group by full_title
#             .annotate(max_price=Max('price_rozn'))  # Get max price for each full_title
#         )
#     except Exception as e:
#         print(f"Error fetching max prices: {e}")
#         return []

# @sync_to_async
# def update_prices(supplier_model, product_field, full_title, max_price):
#     try:
#
#     except Exception as e:
#         print(f"Error updating prices for {full_title}: {e}")


# async def update_max_price_for_supplier(supplier_model, product_field):
#     print(f"Обработка модели: {supplier_model.__name__}")
#
#     # Step 1: Aggregate max prices for each product based on full_title
#     max_prices = await sync_to_async(
#         lambda: list(supplier_model.objects.values(f"{product_field}__full_title").annotate(max_price=Max('price_rozn')))
#     )()
#
#     # Step 2: Create a mapping of full_title to max price
#     product_max_price_map = {
#         entry[f"{product_field}__full_title"]: entry['max_price']
#         for entry in max_prices
#     }
#
#     # Step 3: Prepare objects for bulk update
#     if product_max_price_map:
#         full_titles = list(product_max_price_map.keys())
#
#         update_objects = supplier_model.objects.filter(
#             **{f"{product_field}__full_title__in": full_titles})
#
#         print(update_objects)
#
#         # Step 4: Update the price for each object
#         for obj in update_objects:
#             obj.price_rozn = product_max_price_map.get(obj.full_title, obj.price_rozn)  # Обновляем цену
#
#         # Step 5: Bulk update
#         try:
#             async with transaction.atomic():
#                 await supplier_model.objects.bulk_update(update_objects, ['price_rozn'])
#             print("Обновление завершено.")
#         except Exception as e:
#             print(f"Ошибка при обновлении: {e}")
#     else:
#         print("Нет объектов для обновления.")
# async def update_max_price_for_supplier(supplier_model, product_field):
#     print(f"Обработка модели: {supplier_model.__name__}")
#
#     # Step 1: Aggregate max prices for each product based on full_title
#     max_prices = await asyncio.to_thread(
#         lambda: list(supplier_model.objects.values(f"{product_field}__full_title").annotate(max_price=Max('price_rozn')))
#     )
#
#     # Step 2: Create a mapping of full_title to max price
#     product_max_price_map = {
#         entry[f"{product_field}__full_title"]: entry['max_price']
#         for entry in max_prices
#     }
#
#     # Step 3: Update all records in bulk
#     update_tasks = []
#     for full_title, max_price in product_max_price_map.items():
#         if max_price is not None:
#             print(f"Запланировано обновление для продукта '{full_title}' с максимальной ценой {max_price}...")
#             update_tasks.append(
#                 asyncio.to_thread(
#                     lambda title=full_title, price=max_price: supplier_model.objects.filter(**{f"{product_field}__full_title": title}).update(price_rozn=price)
#                 )
#             )
#
#     results = await asyncio.gather(*update_tasks, return_exceptions=True)
#
#     # Обработка результатов обновлений
#     for full_title, updated_count in zip(product_max_price_map.keys(), results):
#         if isinstance(updated_count, Exception):
#             print(f"Ошибка при обновлении продукта '{full_title}': {updated_count}")
#         else:
#             print(f"Обновлено записей: {updated_count} для продукта '{full_title}'.")

#
# async def update_max_price_for_supplier(supplier_model, product_field):
#     print(f"Обработка модели: {supplier_model.__name__}")
#
#     # Step 1: Aggregate max prices for each product based on full_title
#     max_prices = await asyncio.to_thread(
#         lambda: list(supplier_model.objects.values(f"{product_field}__full_title").annotate(max_price=Max('price_rozn')))
#     )
#
#     # Step 2: Create a mapping of full_title to max price
#     product_max_price_map = {
#         entry[f"{product_field}__full_title"]: entry['max_price']
#         for entry in max_prices
#     }
#     # Step 3: Perform bulk updates within a transaction
#     for full_title, max_price in product_max_price_map.items():
#         print(full_title, max_price)
#         if max_price is not None:
#             print(f"Запланировано обновление для продукта '{full_title}' с максимальной ценой {max_price}...")
#             updated_count = await asyncio.to_thread(
#                 lambda title=full_title, price=max_price: supplier_model.objects.filter(**{f"{product_field}__full_title": title}).update(price_rozn=price)
#             )
#             print(f"Обновлено записей: {updated_count} для продукта '{full_title}'.")
#
#     print("Все обновления завершены.")


# async def update_max_price_for_supplier(supplier_model, product_field):
#     print(f"Обработка модели: {supplier_model.__name__}")
#
#     # Step 1: Aggregate max prices for each product based on full_title
#     max_prices = await asyncio.to_thread(
#         lambda: list(supplier_model.objects.values(f"{product_field}__full_title").annotate(max_price=Max('price_rozn')))
#     )
#
#     # Step 2: Create a mapping of full_title to max price
#     product_max_price_map = {
#         entry[f"{product_field}__full_title"]: entry['max_price']
#         for entry in max_prices
#     }
#
#     # Step 3: Prepare bulk update data
#     updates = [
#         {
#             'filter': {f"{product_field}__full_title": full_title},
#             'price': max_price
#         }
#         for full_title, max_price in product_max_price_map.items() if max_price is not None
#     ]
#
#     # Step 4: Perform bulk updates within a transaction
#     if updates:
#         # Execute bulk update within a transaction
#         with transaction.atomic():
#             for update in updates:
#                 supplier_model.objects.filter(**update['filter']).update(price_rozn=update['price'])
#
#         print(f"Обновлено записей: {len(updates)}.")
#
#     print(f"Все обновления завершены {supplier_model}.")
# async def update_max_prices_for_all_products():
#     items_models = {
#         TruckDiskSupplier: 'truck_disk',
#         TireSupplier: 'tire',
#         DiskSupplier: 'disk',
#         TruckTireSupplier: 'truck_tire',
#         SpecialTireSupplier: 'special_tire',
#         MotoTireSupplier: 'moto_tire',
#     }
#
#     # Create a list of tasks for each supplier model
#     tasks = [update_max_price_for_supplier(model, product_field) for model, product_field in items_models.items()]
#
#     # Run tasks concurrently
#     await asyncio.gather(*tasks)


# def update_max_price_rozn(full_title):
#     # Находим диск по полному названию
#     disk = Disk.objects.filter(full_title=full_title).first()
#
#     if disk:
#         # Находим максимальную цену розницы среди поставщиков этого диска
#         max_price_rozn = DiskSupplier.objects.filter(disk=disk).aggregate(Max('price_rozn'))['price_rozn__max']
#
#         if max_price_rozn is not None:
#             # Обновляем цену розницы у всех поставщиков этого диска
#             DiskSupplier.objects.filter(disk=disk).update(price_rozn=max_price_rozn)
#             return max_price_rozn
#         else:
#             return "Нет доступных цен розницы для данного диска."
#     else:
#         return "Диск с указанным полным названием не найден."