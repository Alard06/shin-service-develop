import os

from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, FileResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings

from apps.company.forms import CompanyForm
from apps.company.models import Company
from apps.company.utils.processing import get_available_products_for_company
from apps.company.utils.uniqueizer import unique
from apps.suppliers.models import Supplier, CompanySupplier, SpecialTireSupplier, TireSupplier, DiskSupplier, \
    TruckTireSupplier, MotoTireSupplier, TruckDiskSupplier


# Create your views here.
def company_list(request):
    """ Функция для отображения списка всех компаний """
    companies = Company.objects.all()  # Получаем все компании
    return render(request, 'company_list.html', {'companies': companies})


def create_company(request):
    """ Функция для создания новой компании """
    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            form.save()  # Сохраняем новую компанию
            return redirect('company_list')  # Перенаправляем на список компаний
    else:
        form = CompanyForm()

    return render(request, 'create_company.html', {'form': form})

def company_data(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    # Получаем специальные шины для выбранных поставщиков
    suppliers = CompanySupplier.objects.filter(company=company).select_related('supplier')

    special_tires = SpecialTireSupplier.objects.filter(supplier__in=suppliers.values_list('supplier', flat=True))
    tires = TireSupplier.objects.filter(supplier__in=suppliers.values_list('supplier', flat=True))
    moto = MotoTireSupplier.objects.filter(supplier__in=suppliers.values_list('supplier', flat=True))
    disk = DiskSupplier.objects.filter(supplier__in=suppliers.values_list('supplier', flat=True))
    truck = TruckTireSupplier.objects.filter(supplier__in=suppliers.values_list('supplier', flat=True))
    truck_disk = TruckDiskSupplier.objects.filter(supplier__in=suppliers.values_list('supplier', flat=True))

    return render(request, 'company-data.html', {
        'company': company,
        'special_tires': special_tires,  # Специальные шины для выбранных поставщиков
        'tires': tires,  # Шины для выбранных поставщиков
        'disks': disk,  # Диски для выбранных поставщиков
        'moto': moto,  # Мото для выбранных поставщиков
        'trucks': truck,  # Truck для выбранных поставщиков
        'trucks_disk': truck_disk,  # Truck для выбранных поставщиков
    })


def company_detail(request, company_id):
    company = get_object_or_404(Company, id=company_id)

    # Получаем всех поставщиков, связанных с данной компанией
    suppliers = CompanySupplier.objects.filter(company=company).select_related('supplier')

    # Получаем всех поставщиков
    all_suppliers = Supplier.objects.all()

    # Исключаем поставщиков, которые уже связаны с данной компанией
    selected_supplier_ids = suppliers.values_list('supplier_id', flat=True)
    available_suppliers = all_suppliers.exclude(id__in=selected_supplier_ids)
    uploads_dir = os.path.join(settings.MEDIA_ROOT, f'uploads/{company_id}')

    # Check if the uploads directory exists, if not, create it
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)  # Create the directory

    # List all files in the uploads directory
    files = os.listdir(uploads_dir)

    # Filter out directories, keep only files
    files = [f for f in files if os.path.isfile(os.path.join(uploads_dir, f))]
    if request.method == 'POST':
        selected_suppliers = request.POST.getlist('suppliers')

        # Обработка генерации XML
        if 'generate_xml' in request.POST:
            # get_available_products_for_company(company.id)
            return redirect('company_detail', company_id=company.id)  # Перенаправляем обратно

        # Обработка выбора поставщиков и их приоритетов
        if selected_suppliers:
            for supplier_id in selected_suppliers:
                supplier = get_object_or_404(Supplier, id=supplier_id)
                priority = request.POST.get(f'priority_{supplier_id}', 1)  # Получаем приоритет для каждого поставщика
                visual_priority = request.POST.get(f'visual_priority_{supplier_id}', 1)  # Получаем визуальный приоритет

                # Убедитесь, что приоритет и визуальный приоритет корректно сохраняются
                CompanySupplier.objects.update_or_create(
                    company=company,
                    supplier=supplier,
                    defaults={'priority': priority, 'visual_priority': visual_priority}
                )

        # Обработка выбора типов и наличия
        types = request.POST.getlist('types')  # Получаем список выбранных типов
        availability = request.POST.get('availability')  # Получаем выбранное значение наличия
        format = request.POST.get('output_format')
        if types and availability:
            get_available_products_for_company(company_id, types, availability, format)

        return redirect('company_detail', company_id=company.id)  # Перенаправляем обратно на страницу компании

    return render(request, 'company_detail.html', {
        'company': company,
        'suppliers': suppliers,  # Поставщики, связанные с компанией
        'available_suppliers': available_suppliers,  # Поставщики, которые еще не выбраны
        'files': files
    })


def upload_file_company(request, company_id):
    if request.method == 'POST' and request.FILES['file']:
        uploaded_file = request.FILES['file']

        # Define the upload directory based on company_id
        uploads_dir = os.path.join(settings.MEDIA_ROOT, f'uploads/{company_id}')

        # Create the directory if it doesn't exist
        os.makedirs(uploads_dir, exist_ok=True)

        # Save the file in the specified directory
        fs = FileSystemStorage(location=uploads_dir)
        filename = fs.save(uploaded_file.name, uploaded_file)  # Save the file

        return HttpResponse(f"Файл {filename} загружен успешно в {uploads_dir}.")
    return HttpResponse("Ошибка загрузки файла.")


def run_uniqueness_checker(request, company_id):
    if request.method == 'POST':
        company = get_object_or_404(Company, id=company_id)
        file_name = request.POST.get('file_name')
        file_path = os.path.join(settings.MEDIA_ROOT, f"uploads/{company_id}/{file_name}")


        # Get selected product types
        product_types = request.POST.getlist('product_type')  # Retrieve all selected values
        print("Selected product types:", product_types)  # Debug output for selected types
        type_file = request.POST.get('output_format')
        # Call your uniqueness function, passing the selected product types
        path = unique(file_path, company=company, company_id=company_id, product_types=product_types, type_file=type_file)
        print(path)

        # Prepare the processed file for download
        processed_file_path = path  # Use the path directly as it already contains the full path

        # Check if the processed file exists
        if os.path.exists(processed_file_path):
            # Return the file response for download
            response = FileResponse(open(processed_file_path, 'rb'), as_attachment=True,
                                    filename=os.path.basename(processed_file_path))  # Use the original filename
            return response
        else:
            print('Обработанный файл не найден. 404')
            return HttpResponse("Обработанный файл не найден.", status=404)

    return HttpResponse("Метод не поддерживается.", status=405)


def download_file_unique(request):
    if request.method == 'POST':
        file_name = request.POST.get('file_name')
        company_id = request.POST.get('company_id')  # Ensure you pass company_id if needed
        file_path = os.path.join(settings.MEDIA_ROOT, f'uploads/{company_id}/{file_name}')
        print(file_path)
        if os.path.isfile(file_path):
            response = FileResponse(open(file_path, 'rb'), as_attachment=True)
            return response
        else:
            return HttpResponse("Файл не найден.")
    return HttpResponse("Ошибка загрузки файла.")

def delete_file(request, company_id):
    if request.method == 'POST':
        file_name = request.POST.get('file_name')
        uploads_dir = os.path.join(settings.MEDIA_ROOT, f'uploads/{company_id}')  # Ensure company_id is defined
        file_path = os.path.join(uploads_dir, file_name)

        if os.path.isfile(file_path):
            os.remove(file_path)  # Delete the file
            return HttpResponse(f"Файл {file_name} удален.")
        else:
            return HttpResponse(f"Файл {file_name} не найден.")


def add_suppliers_to_company(request, company_id):
    company = get_object_or_404(Company, id=company_id)

    if request.method == 'POST':
        # Получаем строку с идентификаторами и разбиваем её на список
        selected_suppliers = request.POST.get('suppliers', '').split(',')
        priority = request.POST.get('priority')

        if 'add_all' in request.POST:  # Проверяем, была ли нажата кнопка "Добавить всех поставщиков"
            all_suppliers = Supplier.objects.all()  # Получаем всех поставщиков
            for supplier in all_suppliers:
                CompanySupplier.objects.update_or_create(
                    company=company,
                    supplier=supplier,
                    defaults={'priority': priority}
                )
        else:  # Обработка выбранных поставщиков
            for supplier_id in selected_suppliers:
                if supplier_id:  # Проверяем, что идентификатор не пустой
                    supplier = get_object_or_404(Supplier, id=supplier_id)
                    CompanySupplier.objects.update_or_create(
                        company=company,
                        supplier=supplier,
                        defaults={'priority': priority}
                    )

        return redirect('company_detail', company_id=company.id)  # Перенаправляем обратно на страницу компании

    all_suppliers = Supplier.objects.all()  # Получаем всех поставщиков для выбора
    return render(request, 'add_suppliers.html', {
        'company': company,
        'all_suppliers': all_suppliers,
    })
def delete_supplier_company(request, supplier_id, company_id):
    # Attempt to retrieve the CompanySupplier object or return a 404 error if not found
    print(supplier_id, company_id)

    company_supplier = get_object_or_404(CompanySupplier, supplier_id=supplier_id, company_id=company_id)

    if request.method == 'POST':
        # Log the deletion and delete the relationship
        company_supplier.delete()
        messages.success(request, 'Supplier relationship successfully deleted.')
        return redirect('company_detail', company_id=company_id)

    # If the request method is not POST, redirect to the company detail page
    messages.info(request, 'No changes made.')


def edit_company(request, company_id):
    company = get_object_or_404(Company, id=company_id)

    if request.method == 'POST':
        form = CompanyForm(request.POST, instance=company)
        if form.is_valid():
            form.save()
            return redirect('company_detail', company_id=company.id)  # Перенаправляем обратно на страницу компании
    else:
        form = CompanyForm(instance=company)

    return render(request, 'edit_company.html', {'form': form, 'company': company})


def delete_company(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    print(company)
    if request.method == 'POST':
        print('POST')
        company.delete()
        return redirect('company_list')  # Перенаправляем на список компаний после удаления

    return render(request, 'error_delete.html', {'company': company})


def update_company_settings(request, company_id):
    company = get_object_or_404(Company, id=company_id)

    if request.method == 'POST':
        # Получаем данные из формы
        description = request.POST.get('description')
        tags = request.POST.get('tags')
        promotions = request.POST.get('promotions')
        protector = request.POST.get('protector')
        price_multiplier = request.POST.get('price_multiplier')

        # Обновляем поля компании
        company.description = description
        company.tags = tags  # Сохраняем теги как строку
        company.promotion = promotions
        company.protector = protector
        company.price_multiplier = float(price_multiplier)
        company.save()  # Сохраняем изменения

        return redirect('company_detail', company_id=company.id)  # Перенаправляем на страницу компании

    return render(request, 'settings.html', {
        'company': company,
    })


def save_ad_order(request, company_id):
    if request.method == 'POST':
        order = request.POST.get('order')  # Get the order from the form
        if order:
            # Split the order string into a list
            print("Received order:", order)  # Debugging statement
            # Here you can save the order to the database or process it as needed
            company = Company.objects.get(id=company_id)
            company.ad_order = order  # Assuming you have a field to store this
            company.save()
            return redirect('company_detail', company_id=company.id)
    return HttpResponse("Invalid request", status=400)

def sortable_ad_view(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    return render(request, 'sortable_ad.html', {'company': company})