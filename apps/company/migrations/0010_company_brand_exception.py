# Generated by Django 5.1.2 on 2024-11-13 05:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0009_company_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='brand_exception',
            field=models.TextField(blank=True, null=True),
        ),
    ]