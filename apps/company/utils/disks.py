import xml.etree.ElementTree as ET

from apps.company.utils.general_tools import immutable_data, get_diameter, get_images, ad_order_create, price_rozn_pow, \
    get_type_disk, get_price


def process_data_disks(ads, data, company, uniq_data_id):
    print(data, company, uniq_data_id)
    supplier = data.find('supplier')
    ad_element = ET.SubElement(ads, "Ad")

    # Add sub-elements with text from the ad_data
    ET.SubElement(ad_element, "Id").text = str(data.get('id'))
    ET.SubElement(ad_element, "Brand").text = data.get('brand').replace(' (Nokian Tyres)', '').replace('Double Star',
                                                                                                       'DoubleStar')
    ET.SubElement(ad_element, "Category").text = immutable_data['CATEGORY']
    ET.SubElement(ad_element, "GoodsType").text = immutable_data['GOODS_TYPE']
    ET.SubElement(ad_element, "RimDiameter").text = str(get_diameter(data.get('diameter')))
    ET.SubElement(ad_element, "Quantity").text = immutable_data['Quantity']
    ET.SubElement(ad_element, "Model").text = str(data.get('product'))
    ET.SubElement(ad_element, "CompanyName").text = company.name
    ET.SubElement(ad_element, "ManagerName").text = company.seller
    ET.SubElement(ad_element, "ContactPhone").text = company.telephone_avito
    ET.SubElement(ad_element, "Address").text = company.address
    ET.SubElement(ad_element, "ProductType").text = 'Диски'
    ET.SubElement(ad_element, "Title").text = str(data.get('fullTitle'))
    ET.SubElement(ad_element, "Condition").text = immutable_data['Condition']
    ET.SubElement(ad_element, "AdType").text = immutable_data['AdType']
    ET.SubElement(ad_element, "Price").text = price_rozn_pow(get_price(supplier.get('price_rozn'),
                                                                       data.get('PriceToPublic'),
                                                                       data.get('brand'), company))  # TODO
    ET.SubElement(ad_element, "RimWidth").text = str(data.get('width').replace(',', '.'))
    ET.SubElement(ad_element, "RimDiameter").text = str(get_diameter(data.get('diameter').replace(',', '.')))
    ET.SubElement(ad_element, "RimOffset").text = str(data.get('outfit', ''))  # Добавлено RimOffset
    ET.SubElement(ad_element, "RimBolts").text = str(data.get('boltcount', ''))
    ET.SubElement(ad_element, "RimBoltsDiameter").text = str(data.get('pcd', ''))  # Добавлено RimBoltsDiameter
    ET.SubElement(ad_element, "RimDIA").text = str(data.get('dia', ''))  # Добавлено RimDIA
    ET.SubElement(ad_element, "RimType").text = get_type_disk(data.get('type', ''))  # Добавлено RimType
    images = ET.SubElement(ad_element, "Images")
    get_images_db = get_images(data, company, uniq_data_id=uniq_data_id)
    if get_images_db:
        if type(get_images_db) == list:
            for image_url in get_images_db:
                ET.SubElement(images, "Image", url=image_url)
        else:
            ET.SubElement(images, "Image", url=get_images_db)

    ET.SubElement(ad_element, "Description").text = ad_order_create(fields=(company.ad_order_avito).split(','),
                                                                    data=data, supplier=supplier,
                                                                    company_description=company.description_avito,
                                                                    company_tags=company.tags_avito,
                                                                    company_promotion=company.promotion_avito)
