from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User, Group
from .models import MasterWaybill, Waybill, WarehouseReceipt, ExcelUpload
from django.urls import NoReverseMatch, reverse
from django.template.response import TemplateResponse

# Custom AdminSite to customize the admin header and title
class LogisticsAdminSite(admin.AdminSite):
    site_header = 'Logistics Management'
    site_title = 'Logistics Management Portal'
    index_title = 'Welcome to Logistics Management Portal'

    def get_app_list(self, request, app_label=None):
        """
        Return a sorted list of all the installed apps that have been
        registered in this site.
        """
        app_dict = self._build_app_dict(request, app_label)

        # Sort the apps alphabetically.
        app_list = sorted(app_dict.values(), key=lambda x: x['name'].lower())

        return app_list

    def index(self, request, extra_context=None):
        """
        Display the main admin index page.
        """
        app_list = self.get_app_list(request)
        context = {
            **self.each_context(request),
            'title': self.index_title,
            'subtitle': None,
            'app_list': app_list,
            **(extra_context or {}),
        }

        return TemplateResponse(request, self.index_template or [
            'admin/index.html',
        ], context)

    def app_index(self, request, app_label, extra_context=None):
        app_list = self.get_app_list(request, app_label)
        if not app_list:
            raise Http404('The requested admin page does not exist.')
        
        context = {
            **self.each_context(request),
            'title': f'{app_label.title()} Administration',
            'subtitle': None,
            'app_list': app_list,
            'app_label': app_label,
            **(extra_context or {}),
        }

        return TemplateResponse(request, self.app_index_template or [
            f'admin/{app_label}/app_index.html',
            'admin/app_index.html',
        ], context)

# Create custom admin site instance
admin_site = LogisticsAdminSite(name='logistics_admin')

class WarehouseReceiptInline(admin.TabularInline):
    model = WarehouseReceipt
    extra = 0

class WaybillInline(admin.TabularInline):
    model = Waybill
    extra = 0
    show_change_link = True

class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_groups')
    list_filter = ('is_staff', 'is_superuser', 'groups')
    
    def get_groups(self, obj):
        return ", ".join([group.name for group in obj.groups.all()])
    get_groups.short_description = 'Groups'

class GroupAdmin(admin.ModelAdmin):
    list_display = ('name',)
    filter_horizontal = ('permissions',)
    exclude = ('permissions',)

class MasterWaybillAdmin(admin.ModelAdmin):
    list_display = ('master_waybill_number', 'container_number', 'created_at', 'created_by')
    search_fields = ('master_waybill_number', 'container_number')
    list_filter = ('created_at', 'created_by')
    ordering = ('-created_at',)
    inlines = [WaybillInline]

    def has_module_permission(self, request):
        return request.user.groups.filter(name__in=['Viewer', 'Uploader']).exists() or request.user.is_superuser

class WaybillAdmin(admin.ModelAdmin):
    list_display = ('waybill_number', 'master_waybill', 'consignee', 'total_packages', 'total_weight', 'total_volume', 'created_at')
    search_fields = ('waybill_number', 'consignee')
    list_filter = ('created_at', 'master_waybill')
    ordering = ('-created_at',)
    inlines = [WarehouseReceiptInline]

    def has_module_permission(self, request):
        return request.user.groups.filter(name__in=['Viewer', 'Uploader']).exists() or request.user.is_superuser

class WarehouseReceiptAdmin(admin.ModelAdmin):
    list_display = ('warehouse_receipt', 'waybill', 'whr_shipper', 'packages', 'weight', 'volume', 'tracking_number', 'created_at')
    search_fields = ('warehouse_receipt', 'whr_shipper', 'tracking_number')
    list_filter = ('created_at',)
    ordering = ('-created_at',)

    def has_module_permission(self, request):
        return request.user.groups.filter(name__in=['Viewer', 'Uploader']).exists() or request.user.is_superuser

class ExcelUploadAdmin(admin.ModelAdmin):
    list_display = ('created_by', 'created_at', 'status', 'admin_notes')
    list_filter = ('status', 'created_at')
    ordering = ('-created_at',)
    
    def get_fields(self, request, obj=None):
        if request.user.is_superuser:
            return ('file', 'created_by', 'created_at', 'status', 'admin_notes')
        # For Uploader users, only show file field for new uploads
        if obj is None:  # New upload
            return ('file',)
        # For existing uploads, show read-only fields
        return ('file', 'created_at', 'status', 'admin_notes')
    
    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return ('created_by', 'created_at', 'file')
        if obj is None:  # New upload
            return ()
        # For existing uploads, all fields are read-only for uploaders
        return ('file', 'created_at', 'status', 'admin_notes')
    
    def has_module_permission(self, request):
        return request.user.groups.filter(name='Uploader').exists() or request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.groups.filter(name='Uploader').exists()

    def has_change_permission(self, request, obj=None):
        if obj is None:
            return True
        if request.user.is_superuser:
            return True
        if obj.created_by == request.user:
            return True
        return False

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return request.user.groups.filter(name='Uploader').exists()
        return obj.created_by == request.user

    def save_model(self, request, obj, form, change):
        if not change:  # If this is a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

# Register models with our custom admin site
admin_site.register(User, UserAdmin)
admin_site.register(Group, GroupAdmin)
admin_site.register(MasterWaybill, MasterWaybillAdmin)
admin_site.register(Waybill, WaybillAdmin)
admin_site.register(WarehouseReceipt, WarehouseReceiptAdmin)
admin_site.register(ExcelUpload, ExcelUploadAdmin)

# Unregister from the default admin site
admin.site.unregister(User)
admin.site.unregister(Group) 