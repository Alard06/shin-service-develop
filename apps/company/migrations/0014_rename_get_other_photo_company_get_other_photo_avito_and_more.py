# Generated by Django 5.1.2 on 2024-11-15 14:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0013_company_get_other_photo'),
    ]

    operations = [
        migrations.RenameField(
            model_name='company',
            old_name='get_other_photo',
            new_name='get_other_photo_avito',
        ),
        migrations.AddField(
            model_name='company',
            name='get_other_photo_drom',
            field=models.BooleanField(default=False),
        ),
    ]
