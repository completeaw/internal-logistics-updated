from django.db import migrations
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from ..models import MasterWaybill, Waybill, WarehouseReceipt, ExcelUpload

def create_groups(apps, schema_editor):
    # Create Viewer group
    viewer_group, _ = Group.objects.get_or_create(name='Viewer')
    
    # Create Uploader group
    uploader_group, _ = Group.objects.get_or_create(name='Uploader')
    
    # Get content types
    master_waybill_ct = ContentType.objects.get_for_model(MasterWaybill)
    waybill_ct = ContentType.objects.get_for_model(Waybill)
    warehouse_receipt_ct = ContentType.objects.get_for_model(WarehouseReceipt)
    excel_upload_ct = ContentType.objects.get_for_model(ExcelUpload)
    
    # Set view permissions for both groups
    view_permissions = Permission.objects.filter(
        content_type__in=[master_waybill_ct, waybill_ct, warehouse_receipt_ct],
        codename__startswith='view_'
    )
    viewer_group.permissions.add(*view_permissions)
    uploader_group.permissions.add(*view_permissions)
    
    # Add additional permissions for Uploader group
    uploader_permissions = Permission.objects.filter(
        content_type=excel_upload_ct,
        codename__in=['add_excelupload', 'change_excelupload', 'view_excelupload']
    )
    uploader_group.permissions.add(*uploader_permissions)
    
    # Add can_upload_excel permission to Uploader group
    can_upload_excel = Permission.objects.get(
        content_type=master_waybill_ct,
        codename='can_upload_excel'
    )
    uploader_group.permissions.add(can_upload_excel)

def reverse_groups(apps, schema_editor):
    Group.objects.filter(name__in=['Viewer', 'Uploader']).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('logistics', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_groups, reverse_groups),
    ] 