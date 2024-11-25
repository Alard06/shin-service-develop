import logging
import math
import xml.etree.ElementTree as ET

import numpy
import pandas as pd
from django.core.exceptions import ObjectDoesNotExist

from apps.services.models import UniqueDetail, UniqueProductNoPhoto
from apps.services.utils.db import add_unique_product_no_photo
from apps.suppliers.models import Tire, Disk, TruckTire, TruckDisk, MotoTire, SpecialTire, TireCompany, \
    TruckTireCompany, TruckDiskCompany, MotoTireCompany, SpecialTireCompany, DiskCompany

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
    formatted_value = str(float(diameter.replace(',', '.'))).rstrip('0').rstrip('.')
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


import logging


def get_images_drom(tires_element, company, uniq_data_id):
    # Initialize logging
    logger = logging.getLogger(__name__)

    # Attempt to find the image in the Tire, Disk, TruckTire, MotoTire, and SpecialTire models
    tire_id = tires_element.get('id')
    models = {
        'Tire': Tire.objects.filter(id_tire=tire_id).first(),
        'Disk': Disk.objects.filter(id_disk=tire_id).first(),
        'TruckTire': TruckTire.objects.filter(id_truck=tire_id).first(),
        'TruckDisk': TruckDisk.objects.filter(id_disk=tire_id).first(),
        'MotoTire': MotoTire.objects.filter(id_moto=tire_id).first(),
        'SpecialTire': SpecialTire.objects.filter(id_special=tire_id).first()
    }

    # Prefetch related company images to reduce queries
    company_models = {
        Tire: TireCompany,
        Disk: DiskCompany,
        TruckTire: TruckTireCompany,
        TruckDisk: TruckDiskCompany,
        MotoTire: MotoTireCompany,
        SpecialTire: SpecialTireCompany
    }

    for model_name, model in models.items():
        if model is not None:
            company_model = company_models.get(model.__class__)
            if company_model is None:
                logger.error(f"No company model found for {model.__class__}")
                continue  # Skip to the next model

            filter_kwargs = {f"{model_name.lower()}": model, "company": company}
            company_image = company_model.objects.filter(**filter_kwargs).first()

            if company_image is not None and company.get_other_photo_drom:
                if company_image.additional_images:
                    return company_image.additional_images
                else:
                    return ' '

            return model.image

    # If no image is found, log the missing element
    logger.warning(f"No image found for element ID: {tires_element.get('brand')} {tires_element.get('product')}")
    element = tires_element
    # Call the async function to add the unique product
    add_unique_product_no_photo(uniq_data_id, element)

    return ' '  # Return empty string if no image found


def get_images_avito(tires_element, company, uniq_data_id):
    # Initialize logging
    logger = logging.getLogger(__name__)
    save_models = None
    # Attempt to find the image in the Tire, Disk, TruckTire, MotoTire, and SpecialTire models
    tire_id = tires_element.get('id')
    models = {
        'Tire': Tire.objects.filter(id_tire=tire_id).first(),
        'Disk': Disk.objects.filter(id_disk=tire_id).first(),
        'TruckTire': TruckTire.objects.filter(id_truck=tire_id).first(),
        'TruckDisk': TruckDisk.objects.filter(id_disk=tire_id).first(),
        'MotoTire': MotoTire.objects.filter(id_moto=tire_id).first(),
        'SpecialTire': SpecialTire.objects.filter(id_special=tire_id).first()
    }

    # Prefetch related company images to reduce queries
    company_models = {
        Tire: TireCompany,
        Disk: DiskCompany,
        TruckTire: TruckTireCompany,
        TruckDisk: TruckDiskCompany,
        MotoTire: MotoTireCompany,
        SpecialTire: SpecialTireCompany
    }
    for model_name, model in models.items():
        if model is not None:
            if company.get_other_photo_avito:
                company_model = company_models.get(model.__class__)
                filter_kwargs = {f"{model_name.lower()}": model, "company": company}
                company_image = company_model.objects.filter(**filter_kwargs).first()
                if company_image is not None and company_image.additional_images:
                    return company_image.additional_images
                else:
                    add_unique_product_no_photo(uniq_data_id, tires_element)
                    image = model.image
                    if image:
                        return model.image
                    else:
                        return ''
            else:
                image = model.image
                if image:
                    return model.image
                else:
                    add_unique_product_no_photo(uniq_data_id, tires_element)
                    return ''


def add_promo_photo(images, company):
    promo_photo = company.promo_photo

    if promo_photo:
        images_string = images
        images_string += f', {promo_photo}'

        return images_string

    return images

def get_images(tires_element, company, drom=False, uniq_data_id=None):
    if drom:
        images = get_images_drom(tires_element, company, uniq_data_id)
        if images and images != ' ':
            images = add_promo_photo(images, company)
    else:
        images = get_images_avito(tires_element, company, uniq_data_id)
        if images and images != ' ':
            images = add_promo_photo(images, company)
    return images


def format_number(num):
    """Formats the number to remove decimal point if it's a whole number."""
    if num.is_integer():
        return str(int(num))
    return str(num)


def generate_tire_size_string(width, height, diameter):
    try:
        diameter = numpy.float16(diameter.replace(',', '.'))
        width = numpy.float16(width.replace(',', '.'))
        try:
            height = numpy.float16(height.replace(',', '.'))
        except:
            height = 'Full'
    except ValueError as e:
        print(f"Error converting tire size: {e}")
        return ""
    diameter_str = format_number(diameter)
    height_str = format_number(height) if height != 'Full' else 'Full'
    width_str = format_number(width)
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
    return ', '.join(sizes)


def ad_order_create(fields, supplier=None, data=None, company_description=None, company_tags=None,
                    company_promotion=None):
    description_parts = []
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

    return '\n\n'.join(description_parts)


def get_price(price_rozn, price_to_public, brand, company):
    brand_exception = company.brand_exception.split(',')
    if brand in brand_exception:
        return float(price_rozn)
    elif price_to_public:
        return float(price_to_public)
    else:
        return float(price_rozn)


def add_other_photo(path, company):
    # Read the Excel file into a DataFrame
    excel_data = pd.read_excel(path)
    data = pd.DataFrame(excel_data, columns=['Наименование', 'Фото'])
    categories = ['Tire', 'Disk', 'SpecialTire', 'MotoTire', 'TruckDisk', 'TruckTire']

    total_processed = 0
    total_added = 0

    for category in categories:
        items = eval(f"{category}.objects.filter(find_images_title__in=data['Наименование'].unique())")
        item_dict = {item.find_images_title.upper(): item for item in items}
        eval(
            f"{category}Company.objects.filter(company=company, {category.lower()}__full_title__in=item_dict.keys()).delete()")

        aggregated_images = {}

        for index, row in data.iterrows():
            item_name = row['Наименование'].upper()
            image = row['Фото']

            if item_name in item_dict:
                if item_name not in aggregated_images:
                    aggregated_images[item_name] = []
                if pd.notna(image):
                    aggregated_images[item_name].append(str(image))
        companies_to_create = []

        for item_name, images in aggregated_images.items():
            item = item_dict[item_name]
            company_instance = eval(f"{category}Company({category.lower()}=item, company=company)")

            company_instance.additional_images = ', '.join(images)
            companies_to_create.append(company_instance)


        total_added += len(companies_to_create)
        eval(f"{category}Company.objects.bulk_create(companies_to_create)")

        total_processed += len(aggregated_images)

    print(f"Total processed items: {total_processed}")
    print(f"Total added items: {total_added}")
