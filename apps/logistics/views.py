from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib import messages
from django.db.models import Sum, Value
from django.db.models.functions import Cast
from django.db.models import DecimalField
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from .models import MasterWaybill, Waybill, WarehouseReceipt, ExcelUpload
from .forms import ExcelUploadForm
from .utils import process_excel_file
import pandas as pd

def is_logistics_user(user):
    """Check if user belongs to either Viewer or Uploader group"""
    return user.is_authenticated and (
        user.groups.filter(name__in=['Viewer', 'Uploader']).exists() or 
        user.is_superuser
    )

def is_uploader(user):
    """Check if user belongs to Uploader group"""
    return user.is_authenticated and (
        user.groups.filter(name='Uploader').exists() or 
        user.is_superuser
    )

@login_required
def master_waybill_list(request):
    """Display list of all master waybills"""
    if not is_logistics_user(request.user):
        raise PermissionDenied("You don't have permission to view this page.")
    
    master_waybills = MasterWaybill.objects.all().order_by('-created_at')
    
    # Calculate totals for each master waybill
    for master_waybill in master_waybills:
        waybills = master_waybill.waybills.all()
        # For packages (now strings), we'll concatenate them
        master_waybill.total_packages = ", ".join(w.total_packages for w in waybills)
        master_waybill.total_weight = waybills.aggregate(Sum('total_weight'))['total_weight__sum'] or 0
        master_waybill.total_volume = waybills.aggregate(Sum('total_volume'))['total_volume__sum'] or 0
    
    context = {
        'master_waybills': master_waybills,
        'can_upload': is_uploader(request.user)
    }
    return render(request, 'logistics/master_waybill_list.html', context)

@login_required
def waybill_summary(request, master_waybill_id):
    """Display summary of waybills for a specific master waybill"""
    if not is_logistics_user(request.user):
        raise PermissionDenied("You don't have permission to view this page.")
    
    master_waybill = get_object_or_404(MasterWaybill, id=master_waybill_id)
    grouped_waybills = master_waybill.get_grouped_waybills()
    
    # Calculate overall totals
    all_waybills = master_waybill.waybills.all()
    totals = {
        'packages': ', '.join(w.total_packages for w in all_waybills),
        'weight': all_waybills.aggregate(Sum('total_weight'))['total_weight__sum'] or 0,
        'volume': all_waybills.aggregate(Sum('total_volume'))['total_volume__sum'] or 0
    }
    
    context = {
        'master_waybill': master_waybill,
        'single_waybills': grouped_waybills['single_waybills'],
        'multiple_waybills': grouped_waybills['multiple_waybills'],
        'totals': totals,
        'can_upload': is_uploader(request.user)
    }
    return render(request, 'logistics/waybill_summary.html', context)

@login_required
def warehouse_receipt_details(request, waybill_id):
    """Display warehouse receipt details for a specific waybill"""
    if not is_logistics_user(request.user):
        raise PermissionDenied("You don't have permission to view this page.")
    
    waybill = get_object_or_404(Waybill, id=waybill_id)
    warehouse_receipts = WarehouseReceipt.objects.filter(waybill=waybill)
    
    context = {
        'waybill': waybill,
        'warehouse_receipts': warehouse_receipts,
        'can_upload': is_uploader(request.user)
    }
    return render(request, 'logistics/warehouse_receipt_details.html', context)

@login_required
def upload_excel(request):
    """Handle Excel file upload and processing"""
    if not is_uploader(request.user):
        raise PermissionDenied("You don't have permission to upload files.")
    
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Save the uploaded file
                excel_upload = ExcelUpload.objects.create(
                    file=form.cleaned_data['file'],
                    created_by=request.user,
                    status='pending'
                )
                
                # Process the file
                success, message = process_excel_file(excel_upload.file.path, request.user)
                
                if success:
                    excel_upload.status = 'approved'
                    excel_upload.save()
                    messages.success(request, 'File processed successfully!')
                    return redirect('logistics:master_waybill_list')
                else:
                    excel_upload.status = 'blocked'
                    excel_upload.admin_notes = message
                    excel_upload.save()
                    messages.error(request, f'Error processing file: {message}')
                
            except Exception as e:
                messages.error(request, f'Error uploading file: {str(e)}')
    else:
        form = ExcelUploadForm()
    
    return render(request, 'logistics/upload_excel.html', {'form': form})

@login_required
def upload_history(request):
    """Display upload history for the current user"""
    if not is_uploader(request.user):
        raise PermissionDenied("You don't have permission to view upload history.")
    
    # For regular uploaders, show only their uploads
    # For superusers, show all uploads
    if request.user.is_superuser:
        uploads = ExcelUpload.objects.all()
    else:
        uploads = ExcelUpload.objects.filter(created_by=request.user)
    
    context = {
        'uploads': uploads,
        'can_upload': True
    }
    return render(request, 'logistics/upload_history.html', context) 