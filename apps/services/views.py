import asyncio
import os
import json
import xml.etree.ElementTree as ET

from django.conf import settings
from django.shortcuts import render, redirect
from django.views import View
from .forms import UploadFileForm
from asgiref.sync import sync_to_async

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .utils.data import tires_elements, disks_elements, truck_tires_element, special_tires_element, moto_tires_element, \
    trucks_disks_elements
from .utils.suppliers import extract_suppliers_and_cities, save_suppliers_and_cities, parse_tire_xml
from ..suppliers.models import Supplier, City, TireSupplier, DiskSupplier, MotoTireSupplier, SpecialTireSupplier, \
    TruckTireSupplier, Tire, Disk, SpecialTire, MotoTire, TruckTire, TruckDiskSupplier, TruckDisk


def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('upload_success')  # Redirect to a success page
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})


def upload_success(request):
    return render(request, 'upload_success.html')


def services_index(request):
    return render(request, 'services_index.html')


def list_files(request):
    # Get the path to the uploads directory
    uploads_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')

    # List all files in the uploads directory
    files = os.listdir(uploads_dir)

    # Filter out directories, keep only files
    files = [f for f in files if os.path.isfile(os.path.join(uploads_dir, f))]

    return render(request, 'services_index.html', {'files': files})


class UploadDataView(View):
    suppliers = None
    cities = None

    async def dispatch(self, request, *args, **kwargs):
        self.suppliers = await self.get_suppliers()
        self.cities = await self.get_cities()
        return await super().dispatch(request, *args, **kwargs)

    async def post(self, request):
        data = json.loads(request.body)
        filename = data.get('filename')

        file_path = os.path.join(settings.MEDIA_ROOT, 'uploads', filename)
        try:
            xml_data = await sync_to_async(self.read_file)(file_path)

            # Удаляем старые данные
            await sync_to_async(self.delete_old_data)()

            # Парсим новые данные
            await self.parse_tire_xml(xml_data, file_path)

            return JsonResponse({'message': 'Данные успешно загружены'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    def read_file(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

    async def get_suppliers(self):
        # Используем sync_to_async для выполнения запроса к базе данных
        suppliers = await sync_to_async(lambda: {supplier.name: supplier for supplier in Supplier.objects.all()})()
        return suppliers

    async def get_cities(self):
        # Используем sync_to_async для выполнения запроса к базе данных
        cities = await sync_to_async(lambda: {city.name: city for city in City.objects.all()})()
        return cities

    def delete_old_data(self):
        # Удаляем старые данные из всех таблиц, кроме поставщиков и компаний
        Disk.objects.all().delete()
        DiskSupplier.objects.all().delete()
        Tire.objects.all().delete()
        TireSupplier.objects.all().delete()
        MotoTire.objects.all().delete()
        MotoTireSupplier.objects.all().delete()
        SpecialTire.objects.all().delete()
        SpecialTireSupplier.objects.all().delete()
        TruckTire.objects.all().delete()
        TruckTireSupplier.objects.all().delete()
        TruckDiskSupplier.objects.all().delete()
        TruckDisk.objects.all().delete()

        print('Старые данные удалены')

    async def parse_tire_xml(self, xml_data, path):
        try:
            root = ET.fromstring(xml_data)
            print('start')
            tasks = [
                special_tires_element(self.suppliers, self.cities, root),
                truck_tires_element(self.suppliers, self.cities, root),
                tires_elements(self.suppliers, self.cities, path),
                moto_tires_element(self.suppliers, self.cities, root),
                disks_elements(self.suppliers, self.cities, root),
                trucks_disks_elements(self.suppliers, self.cities, root)
            ]

            await asyncio.gather(*tasks)
            print('END')
        except Exception as e:
            print(f"An error occurred: {e}")




@csrf_exempt
def delete_file(request):
    if request.method == 'POST':
        try:
            # Load the JSON data from the request body
            data = json.loads(request.body)
            filename = data.get('filename')  # Get the filename from the JSON data

            if filename is None:
                return JsonResponse({'error': 'Filename not provided'}, status=400)

            file_path = os.path.join(settings.MEDIA_ROOT, 'uploads', filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
                return JsonResponse({'success': True})
            return JsonResponse({'error': 'File not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)


@csrf_exempt
def upload_suppliers(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        filename = data.get('filename')
        file_path = os.path.join(settings.MEDIA_ROOT, 'uploads', filename)

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()  # Read the file content
                suppliers = extract_suppliers_and_cities(content)
                print("Extracted suppliers and cities:", suppliers)  # Debugging output
                save_suppliers_and_cities(suppliers)

            return JsonResponse({'content': content})  # Return the content as JSON
        except Exception as e:
            print("Error occurred:", str(e))  # Log the error for debugging
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)
