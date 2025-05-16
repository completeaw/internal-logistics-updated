from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib import messages
from .models import ExcelUpload
from .utils import process_excel_file

@receiver(pre_save, sender=ExcelUpload)
def handle_excel_upload_status_change(sender, instance, **kwargs):
    """Handle status changes for ExcelUpload"""
    if not instance.pk:  # Skip for new instances
        return
        
    try:
        old_instance = ExcelUpload.objects.get(pk=instance.pk)
        
        # If status changed from pending to approved
        if old_instance.status == 'pending' and instance.status == 'approved':
            success, message = process_excel_file(instance.file.path, instance.created_by)
            
            if not success:
                instance.status = 'blocked'
                instance.admin_notes = f"Processing failed: {message}"
            else:
                instance.processed = True
                instance.admin_notes = "File processed successfully"
                
    except ExcelUpload.DoesNotExist:
        pass  # Handle case when instance is new 