from django import forms
from django.forms import modelformset_factory
from .models import Supplier, City, CompanySupplier


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'city']  # Убедитесь, что здесь указаны все необходимые поля

class CompanySupplierForm(forms.ModelForm):
    class Meta:
        model = CompanySupplier
        fields = ['article_number', 'priority', 'visual_priority']

    def __init__(self, *args, **kwargs):
        super(CompanySupplierForm, self).__init__(*args, **kwargs)
        self.fields['article_number'].widget.attrs.update({'class': 'form-control'})
        self.fields['priority'].widget.attrs.update({'class': 'form-check-input'})
        self.fields['visual_priority'].widget.attrs.update({'class': 'form-check-input'})