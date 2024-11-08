from django.urls import path

from apps.index import views

urlpatterns = [
    path('', views.index, name='index')
]
