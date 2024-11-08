# Используем официальный образ Python
FROM python:3.13

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Убедитесь, что вы используете Uvicorn для запуска
CMD ["uvicorn", "core.asgi:application", "--host", "0.0.0.0", "--port", "8000"]