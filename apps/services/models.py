from django.db import models

from django.db import models

from apps.company.models import Company


class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name


class UniqueDetail(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)
    products = models.ManyToManyField('UniqueProductNoPhoto', blank=True)
    date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    path = models.TextField(blank=True, null=True)

    def __str__(self):
        return str(self.date)


class UniqueProductNoPhoto(models.Model):
    """ Модель для продуктов, у которых нет фото """
    id_product = models.CharField(null=True, blank=True, max_length=100)
    brand = models.CharField(max_length=100, blank=True, null=True)
    product = models.CharField(max_length=100, blank=True, null=True)


class NoPriceRoznProduct(models.Model):
    id_product = models.CharField(null=True, blank=True, max_length=100)
    brand = models.CharField(max_length=100, blank=True, null=True)
    product = models.CharField(max_length=100, blank=True, null=True)
    supplier = models.CharField(max_length=100, blank=True, null=True)


class NoPriceRozn(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    path = models.TextField(blank=True, null=True)
    products = models.ManyToManyField('NoPriceRoznProduct', blank=True)