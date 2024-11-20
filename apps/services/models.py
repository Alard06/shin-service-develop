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
    count_no_photos = models.IntegerField(default=0)
    path = models.TextField(blank=True, null=True)

    def __str__(self):
        return str(self.date)


class UniqueProductNoPhoto(models.Model):
    """ Модель для продуктов, у которых нет фото """
    id_product = models.IntegerField(null=True, blank=True)
    brand = models.CharField(max_length=100, blank=True, null=True)
    product = models.CharField(max_length=100, blank=True, null=True)
