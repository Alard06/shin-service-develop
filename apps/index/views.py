from django.shortcuts import render

from .models import Update


def index(request):
    updates = Update.objects.all().order_by('-created_at')  # Получаем все обновления, отсортированные по дате
    return render(request, 'index.html', {'updates': updates})