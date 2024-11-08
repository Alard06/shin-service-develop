from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.db.models import Q

from .models import Supplier, CompanySupplier, City
from .forms import SupplierForm, CompanySupplierForm


def create_supplier(request):
    if request.method == 'POST':
        supplier_form = SupplierForm(request.POST)

        if supplier_form.is_valid():
            # Сохраняем поставщика
            supplier_form.save()
            return redirect('supplier_list')
        else:
            # Выводим ошибки для отладки
            print(supplier_form.errors)
    else:
        supplier_form = SupplierForm()  # Создаем пустую форму для поставщика

    return render(request, 'create_supplier.html', {
        'supplier_form': supplier_form,
    })


def edit_supplier(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)

    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            return redirect('supplier_list')  # Перенаправление на список поставщиков после сохранения
    else:
        form = SupplierForm(instance=supplier)

    return render(request, 'edit_supplier.html', {'form': form, 'supplier': supplier})


def edit_company_supplier(request, company_supplier_id):
    company_supplier = get_object_or_404(CompanySupplier, id=company_supplier_id)

    if request.method == 'POST':
        form = CompanySupplierForm(request.POST, instance=company_supplier)
        if form.is_valid():
            form.save()
            # Redirect to the company detail page with a query parameter for the active tab
            return HttpResponseRedirect(f"{reverse('company_detail', kwargs={'company_id': company_supplier.company.id})}?tab=suppliers")
    else:
        form = CompanySupplierForm(instance=company_supplier)

    return render(request, 'edit_company_supplier.html', {
        'form': form,
        'company_supplier': company_supplier,
    })
@require_POST
def delete_supplier(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)
    supplier.delete()
    return redirect('company_detail')


def supplier_detail(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)
    # Assuming you have a related model for products
    # products = supplier.product_set.all()  # Adjust according to your product model

    return render(request, 'supplier_detail.html', {'supplier': supplier, 'products': 'test1'})


def supplier_list(request):
    query = request.GET.get('q', '')  # Get the search query from the request
    suppliers = Supplier.objects.all()

    if query:
        suppliers = suppliers.filter(
            Q(name__icontains=query) |
            Q(city__name__icontains=query)  # Assuming you have a related name for city
        ).distinct()

    return render(request, 'supplier_list.html', {'suppliers': suppliers, 'query': query})


def add_suppliers_to_company(request, company_id):
    if request.method == 'POST':
        suppliers = request.POST.getlist('suppliers')  # Получаем список выбранных поставщиков
        for supplier_id in suppliers:
            priority = request.POST.get(f'priority_{supplier_id}')  # Получаем приоритет для данного поставщика
            visual_priority = request.POST.get(f'visual_priority_{supplier_id}')  # Получаем визуальный приоритет

            # Проверяем, что приоритет и визуальный приоритет не пустые
            if priority and visual_priority:
                # Создаем или обновляем запись в модели CompanySupplierPriority
                CompanySupplier.objects.update_or_create(
                    company_id=company_id,
                    supplier_id=supplier_id,
                    defaults={
                        'priority': priority,
                        'visual_priority': visual_priority,
                    }
                )
            else:
                # Логируем или обрабатываем случай, когда приоритет не был указан
                print(f"Приоритет или визуальный приоритет не указан для поставщика {supplier_id}")

        return redirect('supplier_list')  # Перенаправление после сохранения
