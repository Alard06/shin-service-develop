from django.db import models


class Company(models.Model):
    """ Модель компании """
    PROTECTOR_CHOICES_DROM = [
        ('cancel', 'Не выбрано'),
        ('all_season', 'Всесезонный'),
        ('summer', 'Лето'),
        ('winter', 'Зима'),
        ('winter_spikes', 'Зима/Шипы'),
    ]
    PROTECTOR_CHOICES_AVITO = [
        ('cancel', 'Не выбрано'),
        ('all_season', 'Всесезонный'),
        ('summer', 'Лето'),
        ('winter', 'Зимние нешипованные'),
        ('winter_spikes', 'Зимние шипованные'),
    ]

    name = models.CharField(max_length=100, unique=True, verbose_name='Company Name')
    description = models.TextField(null=True, blank=True)
    tags = models.CharField(max_length=255, null=True, blank=True)
    promotion = models.TextField(null=True, blank=True)
    protector = models.CharField(max_length=20, choices=PROTECTOR_CHOICES_DROM, null=True, blank=True)
    ad_order = models.TextField(null=True, blank=True)
    price_multiplier = models.FloatField(null=True, blank=True, default=1.0)

    description_avito = models.TextField(null=True, blank=True)
    tags_avito = models.CharField(max_length=255, null=True, blank=True)
    promotion_avito = models.TextField(null=True, blank=True)
    protector_avito = models.CharField(max_length=20, choices=PROTECTOR_CHOICES_AVITO, null=True, blank=True)
    ad_order_avito = models.TextField(null=True, blank=True)
    price_multiplier_avito = models.FloatField(null=True, blank=True, default=1.0)
    telephone_avito = models.CharField(max_length=20, null=True, blank=True)
    seller = models.CharField(max_length=20, null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)

    format_xlsx = models.CharField(max_length=255, null=True, blank=True)

    brand_exception = models.TextField(null=True, blank=True, default=None)
    promo_photo = models.TextField(null=True, blank=True)

    get_other_photo_drom = models.BooleanField(default=False)
    get_other_photo_avito = models.BooleanField(default=False)

    def __str__(self):
        return self.name


