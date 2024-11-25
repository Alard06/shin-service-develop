from apps.company.utils.general_tools import season_to_protector, immutable_data, price_rozn_pow, get_images, \
    ad_order_create, types_avito_tires, get_diameter, get_price
import xml.etree.ElementTree as ET
import openpyxl

def unique_tire_avito(tires, company, season=True):
    ...


def process_data_tire(ads, data, company, uniq_data_id, season=False):
    season_protector = types_avito_tires(data.get('season'))

    if season and not (company.protector_avito == 'cancel'):
        tire_season = types_avito_tires(data.get('season'))
        print(company.protector_avito, season_to_protector, season_to_protector.get(tire_season), tire_season)
        if company.protector_avito not in season_to_protector.get(tire_season):
            print(season_to_protector.get(tire_season), data.get('season'))
            return None
        else:
            season_protector = types_avito_tires(data.get('season'))

    supplier = data.find('supplier')
    ad_element = ET.SubElement(ads, "Ad")

    # Add sub-elements with text from the ad_data
    ET.SubElement(ad_element, "Id").text = str(data.get('id'))
    ET.SubElement(ad_element, "Brand").text = data.get('brand').replace(' (Nokian Tyres)', '').replace(
        'Double Star', 'DoubleStar')
    ET.SubElement(ad_element, "Category").text = immutable_data['CATEGORY']
    ET.SubElement(ad_element, "GoodsType").text = immutable_data['GOODS_TYPE']
    ET.SubElement(ad_element, "RimDiameter").text = str(get_diameter(data.get('diameter')))
    ET.SubElement(ad_element, "TireSectionWidth").text = str(data.get('width').replace(',', '.'))
    ET.SubElement(ad_element, "TireAspectRatio").text = str(data.get('height').replace(',', '.'))
    ET.SubElement(ad_element, "TireType").text = season_protector
    ET.SubElement(ad_element, "Quantity").text = immutable_data['Quantity']
    ET.SubElement(ad_element, "RunFlat").text = str(data.get('runflat'))
    ET.SubElement(ad_element, "Model").text = str(data.get('product'))
    ET.SubElement(ad_element, "CompanyName").text = company.name
    ET.SubElement(ad_element, "ManagerName").text = company.seller
    ET.SubElement(ad_element, "ContactPhone").text = company.telephone_avito
    ET.SubElement(ad_element, "Address").text = company.address
    ET.SubElement(ad_element, "ProductType").text = immutable_data['ProductTypeTire']
    ET.SubElement(ad_element, "Title").text = str(data.get('fullTitle') + " " + season_protector)
    ET.SubElement(ad_element, "Condition").text = immutable_data['Condition']
    ET.SubElement(ad_element, "AdType").text = immutable_data['AdType']
    ET.SubElement(ad_element, "Price").text = price_rozn_pow(get_price(supplier.get('price_rozn'),
                                                                       data.get('PriceToPublic'),
                                                                       data.get('brand'), company))  # TODO
    images = ET.SubElement(ad_element, "Images")
    get_images_db = get_images(data, company, uniq_data_id)
    if get_images_db:
        if type(get_images_db) == list:
            for image_url in get_images_db[::-1]:
                ET.SubElement(images, "Image", url=str(image_url))
        else:
            ET.SubElement(images, "Image", url=str(get_images_db))

    ET.SubElement(ad_element, "Description").text = ad_order_create(fields=(company.ad_order_avito).split(','),
                                                                    data=data, supplier=supplier,
                                       company_description=company.description_avito,
                                       company_tags=company.tags_avito,
                                       company_promotion=company.promotion_avito)


# def get_other_photo(path):
#     with
