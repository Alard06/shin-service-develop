from django.db import models

from apps.company.models import Company


class City(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Supplier(models.Model):
    """ Модель поставщика """
    name = models.CharField(max_length=100, unique=True, verbose_name='Name')
    city = models.ForeignKey(City, on_delete=models.CASCADE)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class CompanySupplier(models.Model):
    """ Модель для хранения индивидуального артикула поставщика для каждой компании """
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    article_number = models.CharField(max_length=100, verbose_name='Article Number', blank=True, null=True)
    priority = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], default=1, null=True, blank=True)
    visual_priority = models.IntegerField(choices=[(1, 'Зеленый'), (2, 'Желтый'), (3, 'Красный')], default=3, null=True,
                                          blank=True)

    class Meta:
        unique_together = ('company', 'supplier')
        ordering = ['-priority', '-visual_priority']

    def __str__(self):
        return f"{self.company.name} - {self.supplier.name} - Article: {self.article_number} - Priority: {self.priority} - Visual: {self.visual_priority}"


class Tire(models.Model):
    """ Модель для хранения информации о шинах """
    id_tire = models.CharField(max_length=100, blank=True, null=True)
    brand = models.CharField(max_length=100)
    brand_article = models.CharField(max_length=100, blank=True, null=True)
    product = models.CharField(max_length=100)
    image = models.URLField()
    full_title = models.CharField(max_length=255)
    model = models.CharField(max_length=100)
    width = models.CharField(max_length=20)
    height = models.CharField(max_length=20)
    diameter = models.CharField(max_length=20)
    season = models.CharField(max_length=20)
    spike = models.BooleanField(default=False)
    runflat = models.BooleanField(default=False)
    lightduty = models.BooleanField(default=False)
    indexes = models.CharField(max_length=10)
    system = models.CharField(max_length=100, blank=True, null=True)
    omolagation = models.CharField(max_length=100, blank=True, null=True)
    mud = models.CharField(max_length=100, blank=True, null=True)
    at = models.CharField(max_length=100, blank=True, null=True)
    runFlatTitle = models.CharField(max_length=100, blank=True, null=True)
    fr = models.CharField(max_length=100, blank=True, null=True)
    xl = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.brand} {self.product} ({self.model})"


class TireSupplier(models.Model):
    """ Модель для хранения информации о поставщиках шин """
    tire = models.ForeignKey(Tire, on_delete=models.CASCADE)
    articul = models.CharField(max_length=100)
    price = models.CharField(max_length=100)
    input_price = models.CharField(max_length=100)  # TODO
    quantity = models.IntegerField()
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    presence = models.CharField(max_length=100)
    delivery_period_days = models.IntegerField()
    last_availability_date = models.DateTimeField()
    sale = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.tire} - {self.supplier.name} - Price: {self.price}"


class Disk(models.Model):
    """ Модель для хранения информации о дисках """
    id_disk = models.CharField(max_length=100, blank=True, null=True)
    brand_articul = models.CharField(max_length=255, blank=True, null=True)  # Артикул бренда
    brand = models.CharField(max_length=100)  # Бренд диска
    product = models.CharField(max_length=100)  # Название продукта
    image = models.URLField()  # URL изображения
    full_title = models.CharField(max_length=255)  # Полное название
    model = models.CharField(max_length=100)  # Модель
    width = models.CharField(max_length=20)
    diameter = models.CharField(max_length=20)
    pcd = models.CharField(max_length=20)
    boltcount = models.CharField(max_length=20)  # Количество болтов
    outfit = models.CharField(max_length=20)
    dia = models.CharField(max_length=20)
    color = models.CharField(max_length=50)  # Цвет
    type = models.CharField(max_length=50)  # Тип (литой, штампованный и т.д.)

    def __str__(self):
        return f"{self.brand} {self.product} ({self.model})"


class DiskSupplier(models.Model):
    """ Модель для хранения информации о поставщиках дисков """
    disk = models.ForeignKey(Disk, on_delete=models.CASCADE)  # Внешний ключ на таблицу Disk
    articul = models.CharField(max_length=100)  # Артикул поставщика
    price = models.CharField(max_length=100)
    input_price = models.CharField(max_length=100)  # Закупочная цена
    quantity = models.CharField(max_length=100)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)  # Внешний ключ на таблицу Supplier
    city = models.ForeignKey(City, on_delete=models.CASCADE)  # Внешний ключ на таблицу City
    presence = models.CharField(max_length=100)  # Наличие
    delivery_period_days = models.CharField(max_length=100)
    last_availability_date = models.DateTimeField()  # Дата последнего наличия
    sale = models.CharField(max_length=20)  # Признак распродажи

    def __str__(self):
        return f"{self.disk} - {self.supplier.name} - Price: {self.price}"


class TruckTire(models.Model):
    """ Модель для хранения информации о грузовых шинах """
    id_truck = models.CharField(max_length=100, blank=True, null=True)
    brand_articul = models.CharField(max_length=255, blank=True, null=True)  # Артикул бренда
    brand = models.CharField(max_length=100)  # Бренд шины
    product = models.CharField(max_length=100)  # Название продукта
    image = models.URLField()  # URL изображения
    full_title = models.CharField(max_length=255)  # Полное название
    model = models.CharField(max_length=100)  # Модель
    width = models.CharField(max_length=100)  # Ширина
    height = models.CharField(max_length=100)  # Высота
    diameter = models.CharField(max_length=100)  # Диаметр
    number_of_plies = models.CharField(max_length=100, null=True, blank=True)  # Количество слоев
    axis = models.CharField(max_length=50)  # Ось
    season = models.CharField(max_length=50)  # Сезон
    indexes = models.CharField(max_length=20)  # Индексы
    quadro = models.BooleanField(default=False)  # Признак квадро
    lightduty = models.CharField(max_length=20)  # Признак легкой нагрузки
    special = models.CharField(max_length=20)  # Признак специального назначения

    def __str__(self):
        return f"{self.brand} {self.product} ({self.model})"


class TruckTireSupplier(models.Model):
    """ Модель для хранения информации о поставщиках грузовых шин """
    truck_tire = models.ForeignKey(TruckTire, on_delete=models.CASCADE)  # Внешний ключ на таблицу TruckTire
    articul = models.CharField(max_length=100)  # Артикул поставщика
    price = models.CharField(max_length=100)  # Цена
    input_price = models.CharField(max_length=100)  # Закупочная цена
    quantity = models.IntegerField()  # Количество
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)  # Внешний ключ на таблицу Supplier
    city = models.ForeignKey(City, on_delete=models.CASCADE)  # Внешний ключ на таблицу City
    presence = models.CharField(max_length=100)  # Наличие
    delivery_period_days = models.IntegerField()  # Срок доставки в днях
    last_availability_date = models.DateTimeField()  # Дата последнего наличия
    sale = models.CharField(max_length=20)  # Признак распродажи

    def __str__(self):
        return f"{self.truck_tire} - {self.supplier.name} - Price: {self.price}"


class TruckDisk(models.Model):
    """ Модель для хранения информации о дисках грузовых машин """
    id_disk = models.CharField(max_length=100, blank=True, null=True)  # ID диска
    brand_articul = models.CharField(max_length=255, blank=True, null=True)  # Артикул бренда
    brand = models.CharField(max_length=100)  # Бренд диска
    product = models.CharField(max_length=100)  # Название продукта
    image = models.URLField()  # URL изображения
    full_title = models.CharField(max_length=255)  # Полное название
    model = models.CharField(max_length=100)  # Модель
    width = models.CharField(max_length=100)  # Ширина
    diameter = models.CharField(max_length=100)  # Диаметр
    pcd = models.CharField(max_length=100)  # PCD (расстояние между болтами)
    boltcount = models.CharField(max_length=100)  # Количество болтов
    outfit = models.CharField(max_length=100)  # Вынос
    dia = models.CharField(max_length=100)  # Диаметр центрального отверстия
    color = models.CharField(max_length=50)  # Цвет
    note = models.CharField(max_length=255, blank=True, null=True)  # Примечание
    type = models.CharField(max_length=50)  # Тип (литой, штампованный и т.д.)

    def __str__(self):
        return f"{self.brand} {self.product} ({self.model})"


class TruckDiskSupplier(models.Model):
    """ Модель для хранения информации о поставщиках специальных шин """
    truck_disk = models.ForeignKey(TruckDisk, on_delete=models.CASCADE)  # Внешний ключ на таблицу SpecialTire
    articul = models.CharField(max_length=100)  # Артикул поставщика
    price = models.CharField(max_length=100)  # Цена
    input_price = models.CharField(max_length=100)  # Закупочная цена
    quantity = models.IntegerField()  # Количество
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)  # Внешний ключ на таблицу Supplier
    city = models.ForeignKey(City, on_delete=models.CASCADE)  # Внешний ключ на таблицу City
    presence = models.CharField(max_length=100)  # Наличие
    delivery_period_days = models.IntegerField()  # Срок доставки в днях
    last_availability_date = models.DateTimeField()  # Дата последнего наличия
    sale = models.CharField(max_length=20)  # Признак распродажи

    def __str__(self):
        return f"{self.truck_disk} - {self.supplier.name} - Price: {self.price}"



class SpecialTire(models.Model):
    """ Модель для хранения информации о специальных шинах """
    id_special = models.CharField(max_length=100, blank=True, null=True)
    brand_articul = models.CharField(max_length=255, blank=True, null=True)  # Артикул бренда
    brand = models.CharField(max_length=100)  # Бренд шины
    product = models.CharField(max_length=100)  # Название продукта
    image = models.URLField()  # URL изображения
    full_title = models.CharField(max_length=255)  # Полное название
    model = models.CharField(max_length=100)  # Модель
    diameter = models.CharField(max_length=20)  # Диаметр
    typesize = models.CharField(max_length=50)  # Размер
    kit = models.CharField(max_length=50)  # Комплект
    indexes = models.CharField(max_length=20, blank=True)  # Индексы
    layers = models.CharField(max_length=10)  # Количество слоев
    camera = models.CharField(max_length=10)  # Камера
    diagonal = models.CharField(max_length=20)  # Признак диагональной шины
    solid = models.CharField(max_length=20)  # Признак сплошной шины
    note = models.TextField(blank=True)  # Примечание
    countries = models.TextField(blank=True)  # Страны
    protector_type = models.CharField(max_length=50, blank=True)  # Тип протектора

    def __str__(self):
        return f"{self.brand} {self.product} ({self.model})"


class SpecialTireSupplier(models.Model):
    """ Модель для хранения информации о поставщиках специальных шин """
    special_tire = models.ForeignKey(SpecialTire, on_delete=models.CASCADE)  # Внешний ключ на таблицу SpecialTire
    articul = models.CharField(max_length=100)  # Артикул поставщика
    price = models.CharField(max_length=100)  # Цена
    input_price = models.CharField(max_length=100)  # Закупочная цена
    quantity = models.IntegerField()  # Количество
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)  # Внешний ключ на таблицу Supplier
    city = models.ForeignKey(City, on_delete=models.CASCADE)  # Внешний ключ на таблицу City
    presence = models.CharField(max_length=100)  # Наличие
    delivery_period_days = models.IntegerField()  # Срок доставки в днях
    last_availability_date = models.DateTimeField()  # Дата последнего наличия
    sale = models.CharField(max_length=20)  # Признак распродажи

    def __str__(self):
        return f"{self.special_tire} - {self.supplier.name} - Price: {self.price}"


class MotoTire(models.Model):
    """ Модель для хранения информации о мотоциклетных шинах """
    id_moto = models.CharField(max_length=100, blank=True, null=True)
    brand_articul = models.CharField(max_length=255, blank=True)  # Артикул бренда
    brand = models.CharField(max_length=100)  # Бренд шины
    product = models.CharField(max_length=100)  # Название продукта
    image = models.URLField()  # URL изображения
    full_title = models.CharField(max_length=255)  # Полное название
    width = models.CharField(max_length=100)  # Ширина
    height = models.CharField(max_length=100)  # Высота
    diameter = models.CharField(max_length=100)  # Диаметр
    indexes = models.CharField(max_length=20)  # Индексы
    axis = models.CharField(max_length=50)  # Ось
    system = models.CharField(max_length=10, blank=True)  # Система
    volume = models.CharField(max_length=100)  # Объем
    weight = models.CharField(max_length=100)  # Вес
    year = models.CharField(max_length=10, blank=True)  # Год
    camera = models.CharField(max_length=10)  # Камера
    runflat = models.CharField(max_length=20)  # Признак Runflat
    omolagation = models.CharField(max_length=20)  # Омологация

    def __str__(self):
        return f"{self.brand} {self.product} ({self.width}/{self.height} R{self.diameter})"


class MotoTireSupplier(models.Model):
    """ Модель для хранения информации о поставщиках мотоциклетных шин """
    moto_tire = models.ForeignKey(MotoTire, on_delete=models.CASCADE)  # Внешний ключ на таблицу MotoTire
    articul = models.CharField(max_length=100)  # Артикул поставщика
    price = models.CharField(max_length=100)
    input_price = models.CharField(max_length=100)  # Закупочная цена
    quantity = models.IntegerField()  # Количество
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)  # Внешний ключ на таблицу Supplier
    city = models.ForeignKey(City, on_delete=models.CASCADE)  # Внешний ключ на таблицу City
    presence = models.CharField(max_length=100)  # Наличие
    delivery_period_days = models.IntegerField()  # Срок доставки в днях
    last_availability_date = models.DateTimeField()  # Дата последнего наличия
    sale = models.CharField(max_length=20)  # Признак распродажи

    def __str__(self):
        return f"{self.moto_tire} - {self.supplier.name} - Price: {self.price}"
