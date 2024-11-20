import os
from datetime import datetime

from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, FileResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings

from apps.company.forms import CompanyForm, FormatXLSXForm
from apps.company.models import Company
from apps.company.utils.general_tools import add_other_photo
from apps.company.utils.processing import get_available_products_for_company
from apps.company.utils.uniqueizer import unique, unique_avito
from apps.services.models import UniqueDetail, UniqueProductNoPhoto
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


def uniq_drom_settings(request, company_id):
    company = get_object_or_404(Company, id=company_id)

    return render(request, 'company-settings-drom.html', {
        'company': company
    })


def company_brand_exceptions(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    return render(request, 'company-settings-exceptions.html', {
        'company': company
    })


def company_brand_exceptions_data(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    if request.method == 'POST':
        brands = request.POST.get('brand')
        company.brand_exception = brands
        company.save()
    return redirect('company_brand_exceptions', company_id=company.id)


def uniq_avito_settings(request, company_id):
    company = get_object_or_404(Company, id=company_id)

    return render(request, 'company-settings-avito.html', {
        'company': company
    })


def uniq_xlsx_settings(request, company_id):
    company = get_object_or_404(Company, id=company_id)

    # Инициализация поля, если оно пустое
    if not company.format_xlsx:
        company.format_xlsx = ', '.join([field[0] for field in FormatXLSXForm.fields_choices])
        company.save()

    # Получаем выбранные поля из базы данных
    selected_fields = company.format_xlsx.split(', ') if company.format_xlsx else []
    print("Selected fields from DB:", selected_fields)

    if request.method == 'POST':
        form = FormatXLSXForm(request.POST)
        if form.is_valid():
            selected_fields = form.cleaned_data['selected_fields']
            print("Selected fields from form:", selected_fields)
            # Сохраняем выбранные поля как строку, разделенную запятыми
            company.format_xlsx = ', '.join(selected_fields)
            company.save()
            return redirect('uniq_xlsx_settings', company_id=company_id)
    else:
        form = FormatXLSXForm(initial={'selected_fields': selected_fields})

    return render(request, 'company-settings-xlsx.html', {
        'form': form,
        'company': company,
        'selected_fields': selected_fields,
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
        path = None
        # Get selected product types
        product_types = request.POST.getlist('product_type')  # Retrieve all selected values
        print("Selected product types:", product_types)  # Debug output for selected types
        type_file = request.POST.get('output_format')
        trading_platform = request.POST.get('trading_platform')
        processing_by_type_other_software = request.POST.get('Processing-by-other-software')
        # Call your uniqueness function, passing the selected product types
        print(trading_platform)
        new_uniq_data = UniqueDetail.objects.create(company=company, date=datetime.now())
        if trading_platform == 'drom':
            path = unique(file_path, company=company, company_id=company_id, product_types=product_types,
                          type_file=type_file, processing_by_type_other_software=processing_by_type_other_software,
                          uniq_data_id=new_uniq_data.pk)
        elif trading_platform == 'avito':
            path = unique_avito(file_path, company=company, product_types=product_types,
                                type_file=type_file,
                                processing_by_type_other_software=processing_by_type_other_software,
                                uniq_data_id=new_uniq_data.pk)

        # Prepare the processed file for download
        processed_file_path = path  # Use the path directly as it already contains the full path
        new_uniq_data.path = processed_file_path
        new_uniq_data.save()
        if os.path.exists(path):
            # Instead of returning the file, redirect to the results page
            return redirect('result_uniq', company_id=company_id, uniq_data_id=new_uniq_data.pk)
        # Check if the processed file exists
        # if os.path.exists(processed_file_path):
            # Return the file response for download
            #response = FileResponse(open(processed_file_path, 'rb'), as_attachment=True,
             #                       filename=os.path.basename(processed_file_path))  # Use the original filename
           # return response

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


def update_company_avito_settings(request, company_id):
    company = get_object_or_404(Company, id=company_id)

    if request.method == 'POST':
        # Получаем данные из формы
        description = request.POST.get('description')
        tags = request.POST.get('tags')
        promotions = request.POST.get('promotions')
        protector = request.POST.get('protector')
        price_multiplier = request.POST.get('price_multiplier')
        seller = request.POST.get('seller')
        address = request.POST.get('address')
        telephone_avito = request.POST.get('telephone')
        promo_photo = request.POST.get('promo-photo')
        get_other_photo = 'photo_source' in request.POST
        print(get_other_photo)

        if price_multiplier == '' or price_multiplier == 'None' or price_multiplier is None:
            price_multiplier = 1
        # Обновляем поля компании
        company.description_avito = description
        company.tags_avito = tags  # Сохраняем теги как строку
        company.promotion_avito = promotions
        company.protector_avito = protector
        company.price_multiplier_avito = float(price_multiplier)
        company.telephone_avito = telephone_avito
        company.address = address
        company.seller = seller
        company.promo_photo = promo_photo
        company.get_other_photo_avito = get_other_photo
        company.save()  # Сохраняем изменения

        return redirect('uniq_avito_settings', company_id=company.id)  # Перенаправляем на страницу компании

    return render(request, 'settings.html', {
        'company': company,
    })


def update_company_drom_settings(request, company_id):
    company = get_object_or_404(Company, id=company_id)

    if request.method == 'POST':
        # Получаем данные из формы
        description = request.POST.get('description')
        tags = request.POST.get('tags')
        promotions = request.POST.get('promotions')
        protector = request.POST.get('protector')
        price_multiplier = request.POST.get('price_multiplier')
        promo_photo = request.POST.get('promo-photo')
        get_other_photo = 'photo_source' in request.POST
        print(get_other_photo)

        if price_multiplier == '' or price_multiplier == 'None' or price_multiplier is None:
            price_multiplier = 1
        # Обновляем поля компании
        company.description = description
        company.tags = tags  # Сохраняем теги как строку
        company.promotion = promotions
        company.protector = protector
        company.price_multiplier = float(price_multiplier)
        company.promo_photo = promo_photo
        company.get_other_photo_drom = get_other_photo
        company.save()  # Сохраняем изменения

        return redirect('uniq_drom_settings', company_id=company.id)  # Перенаправляем на страницу компании

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


def save_ad_order_avito(request, company_id):
    if request.method == 'POST':
        order = request.POST.get('order')  # Get the order from the form
        if order:
            # Split the order string into a list
            print("Received order:", order)  # Debugging statement
            # Here you can save the order to the database or process it as needed
            company = Company.objects.get(id=company_id)
            company.ad_order_avito = order  # Assuming you have a field to store this
            company.save()
            return redirect('company_detail', company_id=company.id)
    return HttpResponse("Invalid request", status=400)


def sortable_ad_view(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    return render(request, 'sortable_ad.html', {'company': company})


def sortable_ad_view_avito(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    return render(request, 'sortable_ad-avito.html', {'company': company})


def load_photo(request, company_id):
    company = Company.objects.get(id=company_id)
    file_name = request.POST.get('file_name')
    uploads_dir = os.path.join(settings.MEDIA_ROOT, f'uploads/{company_id}')  # Ensure company_id is defined
    file_path = os.path.join(uploads_dir, file_name)
    print(file_path)
    add_other_photo(file_path, company)
    return redirect('company_detail', company_id=company.id)



def result_uniq(request, company_id, uniq_data_id):
    company = get_object_or_404(Company, id=company_id)
    uniq_data = get_object_or_404(UniqueDetail, pk=uniq_data_id)
    products = uniq_data.products.all()
    images = []
    for product in products:
        images.append({
            'id_product': product.id_product,
            'brand': product.brand,
            'product': product.product,
            'image': product.image if hasattr(product, 'image') else None
        })

    return render(request, 'company-result-uniq.html', {
        'company': company,
        'uniq_data': uniq_data,
        'images': images,
        'file_path': uniq_data.path  # Pass the file path to the context
    })
