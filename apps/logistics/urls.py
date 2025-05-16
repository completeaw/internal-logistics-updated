from django.urls import path
from . import views

app_name = 'logistics'

urlpatterns = [
    path('', views.master_waybill_list, name='master_waybill_list'),
    path('upload/', views.upload_excel, name='upload_excel'),
    path('upload/history/', views.upload_history, name='upload_history'),
    path('waybill/<int:master_waybill_id>/', views.waybill_summary, name='waybill_summary'),
    path('warehouse-receipt/<int:waybill_id>/', views.warehouse_receipt_details, name='warehouse_receipt_details'),
] 