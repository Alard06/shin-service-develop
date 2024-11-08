import numpy
import xml.etree.ElementTree as ET
import datetime

from apps.suppliers.models import Tire, Disk, TruckTire, MotoTire, SpecialTire
import openpyxl

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


def read_xml(file_path):
    """Reads the XML file and returns the root element."""
    tree = ET.parse(file_path)
    return tree.getroot()


def format_number(num):
    """Formats the number to remove decimal point if it's a whole number."""
    if num.is_integer():
        return str(int(num))  # Convert to int to remove .0
    return str(num)  # Return as is if it's not a whole number


def generate_tire_size_string(width, height, diameter):
    """Generates a formatted string of tire sizes based on width, height, and diameter."""
    # Convert diameter, height, and width to float16
    try:
        diameter = numpy.float16(diameter)
        width = numpy.float16(width)
        try:
            height = numpy.float16(height)
        except:
            height = 'Full'
    except ValueError as e:
        print(f"Error converting tire size: {e}")
        return ""  # Return an empty string or handle the error as needed

    # Format numbers to remove .0 if applicable
    diameter_str = format_number(diameter)
    height_str = format_number(height) if height != 'Full' else 'Full'
    width_str = format_number(width)

    # Create the different combinations of tire sizes
    sizes = [
        f"{diameter_str} {width_str} {height_str}",
        f"{diameter_str}/{width_str}/{height_str}",
        f"{width_str} {height_str} {diameter_str}",
        f"{width_str} {height_str} R{diameter_str}",
        f"{width_str}/{height_str} {diameter_str}",
        f"{width_str}/{height_str} R{diameter_str}",
        f"{width_str}/{height_str}/{diameter_str}",
        f"{width_str}/{height_str}R{diameter_str}",
        f"{width_str}-{height_str} R{diameter_str}",
        f"{width_str}-{height_str}-{diameter_str}",
        f"{width_str}-{height_str}R{diameter_str}",
        f"{width_str}-{height_str}-R{diameter_str}",
    ]

    # Join the sizes into a single string with a comma and space
    return ', '.join(sizes)

def get_images(tires_element):
    tire = Tire.objects.filter(id_tire=tires_element.get('id')).first()
    if tire is not None:
        image = tire.image
        return image
    disk = Disk.objects.filter(id_disk=tires_element.get('id')).first()
    if disk is not None:
        image = disk.image
        return image
    truck = TruckTire.objects.filter(id_truck=tires_element.get('id')).first()
    if truck is not None:
        image = truck.image
        return image
    moto = MotoTire.objects.filter(id_moto=tires_element.get('id')).first()
    if moto is not None:
        image = moto.image
        return image
    special = SpecialTire.objects.filter(id_special=tires_element.get('id')).first()
    if special is not None:
        image = SpecialTire.image
        return image
def process_tires(tires_element, company, season=False):
    """Processes a single tire element and returns the formatted data."""
    offer = {}
    image = get_images(tires_element)

    # Extracting tire data
    offer['id'] = tires_element.get('id')
    offer['brandArticul'] = tires_element.get('brandArticul', '')  # Default to empty string
    offer['brand'] = tires_element.get('brand')
    offer['product'] = tires_element.get('product')
    offer['image'] = image
    offer['fullTitle'] = tires_element.get('fullTitle')
    offer['headline'] = tires_element.get('headline')
    offer['measurement'] = tires_element.get('measurement')
    offer['recommendedPrice'] = tires_element.get('recommendedPrice', '')  # Default to empty string
    offer['model'] = tires_element.get('model')
    offer['width'] = tires_element.get('width')
    offer['height'] = tires_element.get('height')  # Note: height should be '70' not '7'
    offer['diameter'] = tires_element.get('diameter')
    offer['season'] = tires_element.get('season')
    offer['spike'] = tires_element.get('spike')
    offer['lightduty'] = tires_element.get('lightduty')
    offer['indexes'] = tires_element.get('indexes')
    offer['Countries'] = ' '  # #TODO: Add countries if available
    offer['runflat'] = tires_element.get('runflat')
    offer['ProtectorType'] = ' '  # #TODO: Add protector type if available
    season_to_protector = {
        'Всесезонный': 'all_season',
        'Лето': 'summer',
        'Зима': 'winter',
        'Зима/Шипы': 'winter_spikes'
    }
    if season:
        tire_season = tires_element.get('season')
        if season_to_protector.get(tire_season) != company.protector:
            return None  # Skip this tire if it doesn't match the protector type

    # Extracting supplier data
    supplier = tires_element.find('supplier')
    if supplier is not None:
        offer['supplier-articul'] = supplier.get('supplierTitle', '')  # Default to empty string
        offer['supplier-supplierTitle'] = supplier.get('supplierTitle')
        offer['supplier-quantity'] = supplier.get('quantity')
        offer['supplier-price'] = supplier.get('price')
        offer['supplier-inputPrice'] = supplier.get('inputPrice')
        offer['supplier-price_rozn'] = supplier.get('price_rozn')
        offer['supplier-deliveryPeriodDays'] = supplier.get('deliveryPeriodDays')
        offer['supplier-tireType'] = supplier.get('tireType')
        offer['supplier-stock'] = supplier.get('stock')
        offer['supplier-supplier'] = supplier.get('supplier')
        offer['supplier-presence'] = supplier.get('presence')
        offer['supplier-lastAvailabilityDate'] = supplier.get('lastAvailabilityDate')
        offer['supplier-sale'] = supplier.get('sale')
        offer['supplier-year'] = ' '  # #TODO: Add year if available

    # Construct the supplier description based on ad_order
    ad_order = company.ad_order.split(',') if company.ad_order else []
    description_parts = []
    for field in ad_order:
        if field == 'supplier_article':
            description_parts.append(f"{supplier.get('articul', '')}")
        elif field == 'sizes':
            description_parts.append(f"{generate_tire_size_string(offer.get('width'), offer.get('height'), offer.get('diameter'))}")
        elif field == 'tire_description':
            description_parts.append(f"{offer.get('fullTitle', '')}")
        elif field == 'unique_description':
            description_parts.append(f"{company.description or ''}")
        elif field == 'tags':
            if company.tags != 'None':
                description_parts.append(f"{company.tags or ''}")
        elif field == 'promotion':
            if company.promotion != 'None':
                description_parts.append(f"{company.promotion or ''}")
    offer['supplier-description'] = "\n\n".join(description_parts)  # Join the parts into a single description

    return offer


def process_xml(file_path, company, product_types):
    """Processes the XML file and returns a list of offers."""
    root = read_xml(file_path)
    offers = []
    for product in product_types:
        if product == 'tires':
            for tires in root.findall('Tires'):
                offer = process_tires(tires, company, season=True)
                offers.append(offer)
        elif product == 'disks':
            for disks in root.findall('Disks'):
                offer = process_tires(disks, company)
                offers.append(offer)
        elif product == 'moto_tires':
            for moto_tire in root.findall('motoTire'):
                offer = process_tires(moto_tire, company)
                offers.append(offer)
        elif product == 'special_tires':
            for special_tire in root.findall('specialTire'):
                offer = process_tires(special_tire, company)
                offers.append(offer)
        elif product == 'truck_disks':
            for truck_disk in root.findall('truckDisk'):
                offer = process_tires(truck_disk, company)
                offers.append(offer)
        elif product == 'truck_tires':
            for truck_tire in root.findall('truckTire'):
                offer = process_tires(truck_tire, company, season=True)
                offers.append(offer)
    return offers



def save_to_xml(offers, company_id, type_file):
    """Saves the list of offers to an XML file."""
    root = ET.Element('offers')

    for offer in offers:
        if offer:
            offer_element = ET.SubElement(root, 'offer')
            for key, value in offer.items():
                sub_element = ET.SubElement(offer_element, key)
                sub_element.text = str(value)

    tree = ET.ElementTree(root)
    xml_str = ET.tostring(root, encoding='utf-8', xml_declaration=True).decode('utf-8')
    xml = ET.fromstring(xml_str)

    date = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')

    if type_file == 'xlsx':
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(headers)  # Добавляем заголовки

        for offer in xml.findall('offer'):
            row_data = []
            for header in headers:
                element = offer.find(header)
                # Добавляем значение, даже если оно пустое
                value = element.text.strip() if element is not None and element.text else ''
                row_data.append(value)  # Добавляем значение в row_data
            print(row_data)
            ws.append(row_data)

        name = f'Уникализатор-{date}.xlsx'
        path = f'media/uploads/{company_id}/{name}'
        wb.save(path)

    else:
        name = f'Уникализатор-{date}.xml'
        path = f'media/uploads/{company_id}/{name}'
        with open(path, 'w', encoding='utf-8') as xml_file:
            xml_file.write(xml_str.replace("><", ">\n<"))  # Добавляем переносы строк между элементами

    return path



def unique(file_path, company, company_id, product_types, type_file):
    offers = process_xml(file_path, company, product_types)
    print(offers)
    return save_to_xml(offers, company_id, type_file)
