# Generated by Django 4.2.21 on 2025-05-15 14:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('logistics', '0005_alter_excelupload_options_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='waybill',
            old_name='receiver',
            new_name='consignee',
        ),
    ]
