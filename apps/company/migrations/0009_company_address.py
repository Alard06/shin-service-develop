# Generated by Django 5.1.2 on 2024-11-12 17:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0008_company_format_xlsx_company_seller_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='address',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
