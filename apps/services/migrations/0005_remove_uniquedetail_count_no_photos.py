# Generated by Django 5.1.2 on 2024-11-20 10:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0004_uniquedetail_path'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='uniquedetail',
            name='count_no_photos',
        ),
    ]
