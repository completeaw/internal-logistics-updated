from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from apps.logistics.models import MasterWaybill, Waybill, WarehouseReceipt

class Command(BaseCommand):
    help = 'Creates default groups and assigns permissions'

    def handle(self, *args, **options):
        # Create groups if they don't exist
        viewer_group, _ = Group.objects.get_or_create(name='Viewer')
        uploader_group, _ = Group.objects.get_or_create(name='Uploader')

        # Get content type for MasterWaybill model
        master_waybill_content_type = ContentType.objects.get_for_model(MasterWaybill)

        # Get or create custom permission
        upload_permission, _ = Permission.objects.get_or_create(
            codename='can_upload_excel',
            name='Can upload Excel files',
            content_type=master_waybill_content_type,
        )

        # Get view permissions
        view_permission = Permission.objects.get(
            codename='view_masterwaybill',
            content_type=master_waybill_content_type,
        )

        # Assign permissions to groups
        viewer_group.permissions.add(view_permission)
        
        uploader_group.permissions.add(view_permission)
        uploader_group.permissions.add(upload_permission)

        self.stdout.write(self.style.SUCCESS('Successfully set up groups and permissions')) 