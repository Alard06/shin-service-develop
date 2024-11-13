import xml.etree.ElementTree as ET

from apps.company.utils.general_tools import types_avito_tires, season_to_protector, get_diameter, immutable_data, \
    get_images, ad_order_create, price_rozn_pow, get_price


def process_data_truck_tire_and_special(ads, data, company, season=False):
    season_protector = None

    if season:
        tire_season = types_avito_tires(data.get('season'))
        print(company.protector_avito, season_to_protector, season_to_protector.get(tire_season), tire_season)
        if company.protector_avito not in season_to_protector.get(tire_season):
            print(season_to_protector.get(tire_season), data.get('season'))
            return None
        else:
            season_protector = types_avito_tires(data.get('season'))

    supplier = data.find('supplier')
    ad_element = ET.SubElement(ads, "Ad")
    ET.SubElement(ad_element, "Id").text = str(data.get('id'))
    ET.SubElement(ad_element, "Brand").text = data.get('brand').replace(' (Nokian Tyres)', '').replace('Double Star',
                                                                                                       'DoubleStar')
    ET.SubElement(ad_element, "CompanyName").text = company.name
    ET.SubElement(ad_element, "ManagerName").text = company.seller
    ET.SubElement(ad_element, "ContactPhone").text = company.telephone_avito
    ET.SubElement(ad_element, "Address").text = company.address
    ET.SubElement(ad_element, "TireSectionWidth").text = str(data.get('width').replace(',', '.'))
    ET.SubElement(ad_element, "TireAspectRatio").text = str(data.get('height').replace(',', '.'))
    ET.SubElement(ad_element, "RimDiameter").text = str(get_diameter(data.get('diameter')))
    ET.SubElement(ad_element, "AdType").text = immutable_data['AdType']
    ET.SubElement(ad_element, "ProductType").text = 'Шины для грузовиков и спецтехники'
    ET.SubElement(ad_element, "Condition").text = immutable_data['Condition']
    ET.SubElement(ad_element, "Price").text = price_rozn_pow(get_price(supplier.get('price_rozn'),
                                                                       data.get('PriceToPublic'),
                                                                       data.get('brand'), company))  # TODO
    images = ET.SubElement(ad_element, "Images")
    get_images_db = get_images(data, company)
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