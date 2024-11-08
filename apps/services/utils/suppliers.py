""" В этом файле находятся функции с поставщиками """
import asyncio
import xml.etree.ElementTree as ET

from asgiref.sync import sync_to_async
from django.db import transaction

from apps.services.utils.data import tires_elements, disks_elements, truck_tires_element, special_tires_element, \
    moto_tires_element
from apps.suppliers.models import Supplier, City, CompanySupplier, TireSupplier, Tire, DiskSupplier, Disk, \
    TruckTireSupplier, TruckTire, SpecialTireSupplier, MotoTireSupplier, MotoTire, SpecialTire
import concurrent.futures



def extract_suppliers_and_cities(xml_string):
    supplier_city_map = {}  # Словарь для хранения пар поставщик-город

    # Парсинг XML строки
    root = ET.fromstring(xml_string)

    # Находим все элементы поставщиков
    for supplier in root.findall('.//supplier'):
        title = supplier.get('supplierTitle')
        city = supplier.get('city')

        if title and city:  # Проверяем, что значения не пустые
            supplier_city_map[title] = city  # Сопоставляем поставщика с городом

    return supplier_city_map


def save_suppliers_and_cities(supplier_city_map):
    # Создаем или обновляем города и отслеживаем объекты городов
    city_objects = {}

    for city_name in supplier_city_map.values():
        # Используем get_or_create для избежания дубликатов
        city, created = City.objects.get_or_create(name=city_name)
        city_objects[city_name] = city  # Сохраняем объект города для дальнейшего использования

    # Создаем или обновляем поставщиков
    for supplier_name, city_name in supplier_city_map.items():
        city = city_objects.get(city_name)

        # Создаем или обновляем поставщика
        supplier, created = Supplier.objects.update_or_create(
            name=supplier_name,
            defaults={
                'city': city  # Ассоциируем поставщика с объектом города
            }
        )


async def parse_tire_xml(xml_data):
    try:
        root = ET.fromstring(xml_data)
        suppliers = {supplier.name: supplier for supplier in await sync_to_async(Supplier.objects.all)()}
        cities = {city.name: city for city in await sync_to_async(City.objects.all)()}

        tasks = [
            tires_elements(suppliers, cities, root),
            disks_elements(suppliers, cities, root),
            truck_tires_element(suppliers, cities, root),
            special_tires_element(suppliers, cities, root),
            moto_tires_element(suppliers, cities, root),
        ]

        await asyncio.gather(*tasks)
        print('Данные загрузились успешно!')

    except Exception as e:
        print(f"An error occurred: {e}")
