from django import forms
from .models import Company

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите название компании'}),
        }


class FormatXLSXForm(forms.Form):
    fields_choices = [
        ('company', 'Компания'),
        ('supplier', 'Поставщик'),
        ('article_number', 'Артикул'),
        ('priority', 'Приоритет'),
        ('visual_priority', 'Визуальный приоритет'),
        ('brand', 'Бренд'),
        ('product', 'Продукт'),
        ('model', 'Модель'),
        ('width', 'Ширина'),
        ('height', 'Высота'),
        ('diameter', 'Диаметр'),
        ('season', 'Сезон'),
        ('spike', 'Шипы'),
        ('runflat', 'Runflat'),
        ('lightduty', 'Легкий груз'),
        ('indexes', 'Индексы'),
        ('articul', 'Артикул'),
        ('price', 'Цена'),
        ('input_price', 'Закупочная цена'),
        ('price_rozn', 'Розничная цена'),
        ('quantity', 'Количество'),
        ('city', 'Город'),
        ('presence', 'Наличие'),
        ('delivery_period_days', 'Срок доставки (дни)'),
        ('last_availability_date', 'Дата последнего наличия'),
        ('sale', 'Распродажа'),
    ]

    selected_fields = forms.MultipleChoiceField(
        choices=fields_choices,
        widget=forms.CheckboxSelectMultiple,
        label="Выберите поля для включения в таблицу"
    )

    order = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 6)],
        label="Выберите порядок (1 - самый высокий приоритет)"
    )
