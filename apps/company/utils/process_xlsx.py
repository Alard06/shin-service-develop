import os

import pandas as pd

import xml.etree.ElementTree as ET

from django.conf import settings

from apps.company.models import Company


def process_xml_files(file_names, company_id):
    # Base path for media files
    media_path = os.path.join(settings.MEDIA_ROOT, f"uploads/{company_id}")
    output_file_path = os.path.join(media_path, 'output.xlsx')

    company_instance = Company.objects.get(id=company_id)
    field_names = company_instance.format_xlsx.split(',')

    data_list = []

    for file_name in file_names:
        file_path = os.path.join(media_path, file_name)

        # Parse the XML file
        tree = ET.parse(file_path)
        root = tree.getroot()

        for offer in root.findall('offer'):
            data = {}
            for field in field_names:
                field = field.strip()
                element = offer.find(field)
                data[field] = element.text if element is not None else None
            data_list.append(data)
    df = pd.DataFrame(data_list)

    df.to_excel(output_file_path, index=False)
    return output_file_path