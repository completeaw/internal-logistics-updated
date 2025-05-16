import pandas as pd
import numpy as np
from django.db import transaction
from .models import MasterWaybill, Waybill, WarehouseReceipt

def clean_numeric_value(value):
    """Clean and convert numeric values, handling various formats"""
    if pd.isna(value):
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    try:
        # Remove any commas and extra spaces
        cleaned = str(value).replace(',', '').strip()
        return float(cleaned)
    except (ValueError, TypeError):
        return 0.0

def process_excel_file(file_path, user):
    """Process the uploaded Excel file and create database entries"""
    try:
        # Read Excel file
        df = pd.read_excel(file_path)
        
        # Required columns
        required_columns = [
            'Master Waybill (out)',
            'Container Number',
            'Waybill (out)',
            'Consignee',
            'Package',
            'Pieces',
            'Weight (kg)',
            'Volume (ft³)',
            'Warehouse Receipt',
            'WHR Shipper',
            'Tracking Number'
        ]
        
        # Validate required columns
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return False, f"Missing required columns: {', '.join(missing_columns)}"
        
        # Clean numeric columns
        df['Weight (kg)'] = df['Weight (kg)'].apply(clean_numeric_value)
        df['Volume (ft³)'] = df['Volume (ft³)'].apply(clean_numeric_value)
        df['Pieces'] = df['Pieces'].apply(lambda x: int(clean_numeric_value(x)))
        
        # Group by Master Waybill
        master_waybill_groups = df.groupby('Master Waybill (out)')
        
        with transaction.atomic():  # Add transaction management
            for master_waybill_number, master_group in master_waybill_groups:
                if pd.isna(master_waybill_number):
                    continue  # Skip empty master waybill numbers
                    
                # Get or create MasterWaybill
                try:
                    master_waybill, created = MasterWaybill.objects.get_or_create(
                        master_waybill_number=str(master_waybill_number),
                        defaults={
                            'container_number': str(master_group['Container Number'].iloc[0]),
                            'created_by': user
                        }
                    )
                    
                    # If master waybill exists, update its container number
                    if not created:
                        master_waybill.container_number = str(master_group['Container Number'].iloc[0])
                        master_waybill.save()
                except Exception as e:
                    return False, f"Error with Master Waybill {master_waybill_number}: {str(e)}"
                
                # Group by Waybill within Master Waybill
                waybill_groups = master_group.groupby('Waybill (out)')
                
                for waybill_number, waybill_group in waybill_groups:
                    if pd.isna(waybill_number):
                        continue  # Skip empty waybill numbers
                        
                    # Calculate totals for the waybill
                    try:
                        # Combine Package and Pieces for total packages
                        packages = waybill_group.apply(lambda row: f"{row['Package']} x {row['Pieces']}", axis=1)
                        total_packages = ', '.join(packages)
                        
                        # Sum numeric values
                        total_weight = waybill_group['Weight (kg)'].sum()
                        total_volume = waybill_group['Volume (ft³)'].sum()
                        
                        # Ensure they are valid numbers
                        if not np.isfinite(total_weight) or not np.isfinite(total_volume):
                            return False, f"Invalid numeric values found for waybill {waybill_number}"
                            
                    except Exception as e:
                        return False, f"Error calculating totals for waybill {waybill_number}: {str(e)}"
                    
                    try:
                        # Get or create Waybill
                        waybill, created = Waybill.objects.get_or_create(
                            master_waybill=master_waybill,
                            waybill_number=str(waybill_number),
                            defaults={
                                'consignee': str(waybill_group['Consignee'].iloc[0]),
                                'total_packages': total_packages,
                                'total_weight': total_weight,
                                'total_volume': total_volume
                            }
                        )
                        
                        # If waybill exists, update its details
                        if not created:
                            waybill.consignee = str(waybill_group['Consignee'].iloc[0])
                            waybill.total_packages = total_packages
                            waybill.total_weight = total_weight
                            waybill.total_volume = total_volume
                            waybill.save()
                            
                            # Delete existing warehouse receipts for this waybill
                            waybill.warehouse_receipts.all().delete()
                            
                    except Exception as e:
                        return False, f"Error creating waybill {waybill_number}: {str(e)}"
                    
                    # Create Warehouse Receipts
                    for _, row in waybill_group.iterrows():
                        try:
                            packages_str = f"{row['Package']} x {row['Pieces']}"
                            WarehouseReceipt.objects.create(
                                waybill=waybill,
                                warehouse_receipt=str(row['Warehouse Receipt']),
                                whr_shipper=str(row['WHR Shipper']),
                                packages=packages_str,
                                weight=float(row['Weight (kg)']),
                                volume=float(row['Volume (ft³)']),
                                tracking_number=str(row['Tracking Number'])
                            )
                        except Exception as e:
                            return False, f"Error creating warehouse receipt for waybill {waybill_number}: {str(e)}"
        
        return True, "File processed successfully"
    except pd.errors.EmptyDataError:
        return False, "The Excel file is empty"
    except pd.errors.ParserError:
        return False, "Error reading the Excel file. Please make sure it's a valid Excel file."
    except Exception as e:
        return False, f"Error processing file: {str(e)}" 