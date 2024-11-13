import math
import xml.etree.ElementTree as ET

import numpy

from apps.suppliers.models import Tire, Disk, TruckTire, MotoTire, SpecialTire

immutable_data = {
    'CATEGORY': 'Запчасти и аксессуары',
    'AdType': 'Товар приобретен на продажу',
    'GOODS_TYPE': 'Шины, диски и колёса',
    'Condition': 'Новое',
    'Quantity': 'за 1 шт.',
    'ProductTypeTire': 'Легковые шины'
}

season_to_protector = {
    'Всесезонный': 'all_season',
    'Летние': 'summer',
    'Зимние нешипованные': 'winter',
    'Зимние шипованные': 'winter_spikes'
}


def get_diameter(diameter):
    formatted_value = str(float(diameter)).rstrip('0').rstrip('.')
    return formatted_value


def read_xml(file_path):
    """Reads the XML file and returns the root element."""
    tree = ET.parse(file_path)
    return tree.getroot()


def get_type_disk(type_disk):
    if type_disk == 'Литой':
        return 'Литые'
    elif type_disk == 'Штамповка':
        return 'Штампованные'
    return type_disk


def types_avito_tires(season):
    if season in 'Зима':
        return 'Зимние нешипованные'
    if season in 'Зима / Шипы':
        return 'Зимние шипованные'

    if season in 'Лето':
        return 'Летние'

    if season in 'Всесезонный':
        return 'Всесезонный'


def price_rozn_pow(price_rozn):
    return math.ceil(float(price_rozn))


def get_images(tires_element, company, drom=False):
    tire = Tire.objects.filter(id_tire=tires_element.get('id')).first()
    image = None
    if tire is not None:
        image = tire.image
    disk = Disk.objects.filter(id_disk=tires_element.get('id')).first()
    if disk is not None:
        image = disk.image
    truck = TruckTire.objects.filter(id_truck=tires_element.get('id')).first()
    if truck is not None:
        image = truck.image
    moto = MotoTire.objects.filter(id_moto=tires_element.get('id')).first()
    if moto is not None:
        image = moto.image
    special = SpecialTire.objects.filter(id_special=tires_element.get('id')).first()
    if special is not None:
        image = SpecialTire.image
    print(company.promo_photo)
    if company.promo_photo and not drom:
        data = company.promo_photo.split(',')
        data.append(image)
        return data
    if not drom:
        return image
    print(company.promo_photo)
    if drom and company.promo_photo:
        if image:
            data = image + ', ' + company.promo_photo.replace(',', ', ')
            return data
        return ''
    return image

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


def ad_order_create(fields, supplier=None, data=None, company_description=None, company_tags=None,
                    company_promotion=None):
    description_parts = []
    print(data)
    print(fields)
    for field in fields:
        if field == 'supplier_article':
            description_parts.append(f"{supplier.get('articul', '')}")
        elif field == 'sizes':
            description_parts.append(
                f"{generate_tire_size_string(data.get('width'), data.get('height'), data.get('diameter'))}")
        elif field == 'tire_description':
            description_parts.append(f"{data.get('fullTitle', '')}")
        elif field == 'unique_description':
            description_parts.append(f"{company_description or ''}")
        elif field == 'tags':
            if company_tags != 'None':
                description_parts.append(f"{company_tags or ''}")
        elif field == 'promotion':
            if company_promotion != 'None':
                description_parts.append(f"{company_promotion or ''}")

    print(description_parts)
    return '\n\n'.join(description_parts)


def get_price(price_rozn, price_to_public, brand, company):
    brand_exception = company.brand_exception.split(',')
    if brand in brand_exception:
        return float(price_rozn)
    else:
        return float(price_to_public)