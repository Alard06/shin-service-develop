import xml.etree.ElementTree as ET
from datetime import datetime

import openpyxl

from apps.company.utils.disks import process_data_disks
from apps.company.utils.general_tools import read_xml
from apps.company.utils.motoTIres import process_data_moto
from apps.company.utils.tires import process_data_tire
from apps.company.utils.truckTire import process_data_truck_tire_and_special

headers_drom = [
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

headers_avito_tires = [
    'Address', 'Id', 'Description', 'Category', 'GoodsType', 'AdType', 'ProductType', 'Brand', 'Model',
    'TireSectionWidth', 'RimDiameter', 'TireAspectRatio', 'TireType', 'Quantity', 'TireYear',
    'BackRimDiameter', 'BackTireAspectRatio', 'BackTireSectionWidth', 'ResidualTread', 'Condition'
]


def process_xml_avito(file_path, company, product_types, uniq_data_id):
    print(file_path, company, product_types)
    root = read_xml(file_path)
    print('read')
    ads = ET.Element("Ads", formatVersion="3", target="Avito.ru")
    print('ads')
    for product in product_types:
        if product == 'tires':
            for tires in root.findall('Tires'):
                process_data_tire(ads, tires, company, uniq_data_id, season=True)
        elif product == 'disks':
            for disk in root.findall('Disks'):
                process_data_disks(ads, disk, company, uniq_data_id)
        elif product == 'moto_tires':
            for moto_tire in root.findall('motoTire'):
                process_data_moto(ads, moto_tire, company=company, uniq_data_id=uniq_data_id)
        elif product == 'truck_tires':
            for truck_tire in root.findall('truckTire'):
                process_data_truck_tire_and_special(ads, truck_tire, company, uniq_data_id, season=True)
        elif product == 'special_tires':
            for special_tire in root.findall('specialTire'):
                process_data_truck_tire_and_special(ads, special_tire, company,uniq_data_id, season=True)
        elif product == 'truck_disks':
            for truck_disk in root.findall('truckDisk'):
                process_data_disks(ads, truck_disk, uniq_data_id, company)
    return ads


## TEMP
# TODO
def process_xml_avito_handler(file_path, company, product_types, uniq_data_id):
    root = read_xml(file_path)
    print('read')
    ads = ET.Element("Ads", formatVersion="3", target="Avito.ru")
    print('ads')
    for product in product_types:
        if product == 'tires':
            for tires in root.findall('tires/tire'):
                process_data_tire(ads, tires, company, uniq_data_id, season=True)
        elif product == 'disks':
            for disk in root.findall('disks/disk'):
                process_data_disks(ads, disk, company, uniq_data_id)
        elif product == 'moto_tires':
            for moto_tire in root.findall('moto/motoTire'):
                process_data_moto(ads, moto_tire, company, uniq_data_id)
        elif product == 'truck_tires':
            for truck_tire in root.findall('trucks/truckTire'):
                process_data_truck_tire_and_special(ads, truck_tire, company, uniq_data_id, season=True)
        elif product == 'special_tires':
            for special_tire in root.findall('specialTires/specialTire'):
                process_data_truck_tire_and_special(ads, special_tire, company, uniq_data_id, season=True)
        elif product == 'truck_disks':
            for truck_disk in root.findall('truckDisks/truckDisk'):
                process_data_disks(ads, truck_disk,company, uniq_data_id)
    return ads


def save_to_xml_avito(ads, type_file, company_id, product_types):
    # Преобразуем все значения в строки перед сериализацией
    def convert_to_string(element):
        for child in element:
            if isinstance(child.text, int):
                child.text = str(child.text)  # Преобразуем целое число в строку
            convert_to_string(child)  # Рекурсивно обрабатываем дочерние элементы

    convert_to_string(ads)  # Применяем преобразование к корневому элементу

    xml = ET.tostring(ads, encoding='utf-8', xml_declaration=True).decode('utf-8')
    date = datetime.now().strftime('%Y%m%d-%H%M%S')

    name = f'Уникализатор-AVITO-{date}.xml'
    path = f'media/uploads/{company_id}/{name}'
    with open(path, 'w', encoding='utf-8') as xml_file:
        xml_file.write(xml)  # Записываем XML в файл

    return path
