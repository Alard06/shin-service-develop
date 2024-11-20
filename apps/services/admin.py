from django.contrib import admin

from apps.services.models import UniqueDetail, UniqueProductNoPhoto

# Register your models here.
admin.site.register(UniqueDetail)
admin.site.register(UniqueProductNoPhoto)
