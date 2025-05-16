from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Sum

class MasterWaybill(models.Model):
    master_waybill_number = models.CharField(max_length=100, unique=True)
    container_number = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.master_waybill_number

    def get_grouped_waybills(self):
        """Group waybills by waybill number and calculate totals"""
        waybills = self.waybills.all()
        grouped_waybills = {}
        
        for waybill in waybills:
            if waybill.waybill_number in grouped_waybills:
                group = grouped_waybills[waybill.waybill_number]
                group['waybills'].append(waybill)
                group['total_packages'] = ', '.join([w.total_packages for w in group['waybills']])
                group['total_weight'] += waybill.total_weight
                group['total_volume'] += waybill.total_volume
            else:
                grouped_waybills[waybill.waybill_number] = {
                    'waybills': [waybill],
                    'waybill_number': waybill.waybill_number,
                    'consignee': waybill.consignee,
                    'total_packages': waybill.total_packages,
                    'total_weight': waybill.total_weight,
                    'total_volume': waybill.total_volume,
                    'count': 1
                }
        
        # Convert to list and sort by waybill number
        single_waybills = []
        multiple_waybills = []
        
        for group in grouped_waybills.values():
            if len(group['waybills']) > 1:
                multiple_waybills.append(group)
            else:
                single_waybills.append(group)
        
        return {
            'single_waybills': sorted(single_waybills, key=lambda x: x['waybill_number']),
            'multiple_waybills': sorted(multiple_waybills, key=lambda x: x['waybill_number'])
        }

    class Meta:
        ordering = ['-created_at']
        permissions = [
            ("can_upload_excel", "Can upload excel files"),
        ]

class Waybill(models.Model):
    master_waybill = models.ForeignKey(MasterWaybill, on_delete=models.CASCADE, related_name='waybills')
    waybill_number = models.CharField(max_length=100, unique=True)
    consignee = models.CharField(max_length=200)
    total_packages = models.CharField(max_length=100)
    total_weight = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_volume = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.waybill_number

    class Meta:
        ordering = ['-created_at']

class WarehouseReceipt(models.Model):
    waybill = models.ForeignKey(Waybill, on_delete=models.CASCADE, related_name='warehouse_receipts')
    warehouse_receipt = models.CharField(max_length=100)
    whr_shipper = models.CharField(max_length=200)
    packages = models.CharField(max_length=100)
    weight = models.DecimalField(max_digits=10, decimal_places=2)
    volume = models.DecimalField(max_digits=10, decimal_places=2)
    tracking_number = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.warehouse_receipt

    class Meta:
        ordering = ['-created_at']

class ExcelUpload(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('blocked', 'Blocked')
    ]
    
    file = models.FileField(upload_to='excel_uploads/')
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True, null=True)
    processed = models.BooleanField(default=False)

    def __str__(self):
        return f"Upload by {self.created_by} on {self.created_at}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Excel Upload'
        verbose_name_plural = 'Excel Uploads' 