import logging
import math
import xml.etree.ElementTree as ET

import numpy
import pandas as pd
from django.core.exceptions import ObjectDoesNotExist

from apps.services.models import UniqueDetail, UniqueProductNoPhoto
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
    image = None

    # Attempt to find the image in the Tire, Disk, TruckTire, MotoTire, and SpecialTire models
    models = [
        Tire.objects.filter(id_tire=tires_element.get('id')).first(),
        Disk.objects.filter(id_disk=tires_element.get('id')).first(),
        TruckTire.objects.filter(id_truck=tires_element.get('id')).first(),
        MotoTire.objects.filter(id_moto=tires_element.get('id')).first(),
        SpecialTire.objects.filter(id_special=tires_element.get('id')).first()
    ]

    company_models = [TireCompany, DiskCompany, TruckTireCompany, MotoTireCompany, SpecialTireCompany]

    for model, company_model in zip(models, company_models):
        if model is not None:
            model_field_name = f"{model.__class__.__name__.lower()}"
            filter_kwargs = {model_field_name: model, "company": company}
            company_image = company_model.objects.filter(**filter_kwargs).first()

            if company.get_other_photo_drom:
                print(company_image.additional_images and company.get_other_photo_drom)
                if company_image.additional_images and company.get_other_photo_drom:
                    return company_image.additional_images
                elif company.get_other_photo_drom:
                    return ' '
            else:
                return model.image

    # If no image is found, log the missing element
    if not image or image == ' ':
        try:
            unique_detail = UniqueDetail.objects.get(pk=uniq_data_id)
            unique_detail.count_no_photos += 1  # Increment count of missing photos
            new_product = UniqueProductNoPhoto.objects.create(
                id_product=tires_element.get('id'),
                brand=tires_element.get('brand'),
                product=tires_element.get('product')
            )
            unique_detail.products.add(new_product)  # Use add() to associate the new product
            unique_detail.save()
        except ObjectDoesNotExist:
            logger.error(f"UniqueDetail with id {uniq_data_id} does not exist.")
        logger.warning(f"No image found for element ID: {tires_element.get('brand')} {tires_element.get('product')}")
        return ' '  # Return empty string if no image found

    return ' '  # Ensure we return an empty string if no image found


def get_images_avito(tires_element, company, uniq_data_id=None):
    # Initialize logging
    logger = logging.getLogger(__name__)
    image = None
    model_product = None

    # Attempt to find the image in the Tire, Disk, TruckTire, MotoTire, and SpecialTire models
    models = [
        Tire.objects.filter(id_tire=tires_element.get('id')).first(),
        Disk.objects.filter(id_disk=tires_element.get('id')).first(),
        TruckTire.objects.filter(id_truck=tires_element.get('id')).first(),
        MotoTire.objects.filter(id_moto=tires_element.get('id')).first(),
        SpecialTire.objects.filter(id_special=tires_element.get('id')).first()
    ]

    # Check for images in the primary models
    for model in models:
        if model is not None:
            company_models = [TireCompany, DiskCompany, TruckTireCompany, MotoTireCompany, SpecialTireCompany]
            for company_model in company_models:
                model_field_name = f"{model.__class__.__name__.lower()}"
                model_product = model
                filter_kwargs = {model_field_name: model, "company": company}
                company_image = company_model.objects.filter(**filter_kwargs).first()
                if company_image and company_image.additional_images and company.get_other_photo_avito:
                    image = company_image.additional_images
                    break
                if company.get_other_photo_avito:
                    image = ' '
                    break
                if not company.get_other_photo_avito:
                    image = model.image
                    break
            if image:  # Break if an image is found
                break

    # If no image is found, log the missing element
    if not image or image == ' ':
        try:
            unique_detail = UniqueDetail.objects.get(pk=uniq_data_id)
            unique_detail.count_no_photos += 1  # Increment count of missing photos
            new_product = UniqueProductNoPhoto.objects.create(
                id_product=tires_element.get('id'),
                brand=tires_element.get('brand'),
                product=tires_element.get('product')
            )
            unique_detail.products.add(new_product)  # Use add() to associate the new product
            unique_detail.save()
        except ObjectDoesNotExist:
            logger.error(f"UniqueDetail with id {uniq_data_id} does not exist.")
        logger.warning(f"No image found for element ID: {tires_element.get('brand')} {tires_element.get('product')}")
        return model_product.image
    return image if image else ' '  # Ensure we return an empty string if no image found

def add_promo_photo(images, company):
    """Add the promotional photo to the list of images as a comma-separated string."""
    # Retrieve the promo photo from the company instance
    promo_photo = company.promo_photo

    # Check if the promo photo is not empty or None
    if promo_photo:
        # Join the existing images with the promo photo
        images_string = images  # Convert the list of images to a comma-separated string
        images_string += f', {promo_photo}'  # Append the promo photo

        return images_string  # Return the updated string of images

    return images  # Return the original images if no promo photo is found

def get_images(tires_element, company, drom=False, uniq_data_id=None):
    if drom:
        images = get_images_drom(tires_element, company, uniq_data_id)
        if images and images != ' ':
            images = add_promo_photo(images, company)
    else:
        images = get_images_avito(tires_element, company, uniq_data_id)
    return images


def format_number(num):
    """Formats the number to remove decimal point if it's a whole number."""
    if num.is_integer():
        return str(int(num))  # Convert to int to remove .0
    return str(num)  # Return as is if it's not a whole number


def generate_tire_size_string(width, height, diameter):
    """Generates a formatted string of tire sizes based on width, height, and diameter."""
    # Convert diameter, height, and width to float16
    try:
        diameter = numpy.float16(diameter.replace(',', '.'))
        width = numpy.float16(width.replace(',', '.'))
        try:
            height = numpy.float16(height.replace(',', '.'))
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

    # Define the categories to process
    categories = ['Tire', 'Disk', 'SpecialTire', 'MotoTire', 'TruckDisk', 'TruckTire']

    total_processed = 0
    total_added = 0

    for category in categories:
        # Fetch all items for the current category
        items = eval(f"{category}.objects.filter(find_images_title__in=data['Наименование'].unique())")
        item_dict = {item.find_images_title.upper(): item for item in items}

        # Clear existing instances for the specified company
        eval(
            f"{category}Company.objects.filter(company=company, {category.lower()}__full_title__in=item_dict.keys()).delete()")

        # Prepare a dictionary to hold aggregated image data
        aggregated_images = {}

        for index, row in data.iterrows():
            item_name = row['Наименование'].upper()  # Convert to uppercase
            image = row['Фото']

            if item_name in item_dict:
                # Aggregate images for the same item, ensuring no NaN values are included
                if item_name not in aggregated_images:
                    aggregated_images[item_name] = []
                if pd.notna(image):  # Check if the image is not NaN
                    # Convert image to string if it's not already
                    aggregated_images[item_name].append(str(image))

        # Prepare a list to hold new instances to be created
        companies_to_create = []

        for item_name, images in aggregated_images.items():
            item = item_dict[item_name]

            # Create a new Company instance
            company_instance = eval(f"{category}Company({category.lower()}=item, company=company)")

            # Join images with a comma and update additional_images
            company_instance.additional_images = ', '.join(images)
            companies_to_create.append(company_instance)


        # Bulk create all new instances at once
        total_added += len(companies_to_create)
        eval(f"{category}Company.objects.bulk_create(companies_to_create)")

        # Update total processed items
        total_processed += len(aggregated_images)

    print(f"Total processed items: {total_processed}")
    print(f"Total added items: {total_added}")
