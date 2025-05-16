# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import datetime
import json
from django.template import Context
from django.utils import translation

try:
    from django.apps.registry import apps
except ImportError:
    try:
        from django.apps import apps  # Fix Django 1.7 import issue
    except ImportError:
        pass
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse

try:
    from django.core.urlresolvers import reverse, resolve, NoReverseMatch
except ImportError:  # Django 1.11
    from django.urls import reverse, resolve, NoReverseMatch

from django.contrib.admin import AdminSite
from django.utils.text import capfirst
from django.contrib import messages
from django.contrib.admin.options import IncorrectLookupParameters
from django.contrib import admin
from django.utils.text import slugify

try:
    from django.utils.translation import ugettext_lazy as _
except ImportError:
    from django.utils.translation import gettext_lazy as _  # Django 4.0.0 and more

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict  # Python 2.6


default_apps_icon = {
    'auth': 'fa fa-users'
}


class JsonResponse(HttpResponse):
    """
    An HTTP response class that consumes data to be serialized to JSON.
    :param data: Data to be dumped into json. By default only ``dict`` objects
      are allowed to be passed due to a security flaw before EcmaScript 5. See
      the ``safe`` parameter for more information.
    :param encoder: Should be an json encoder class. Defaults to
      ``django.core.serializers.json.DjangoJSONEncoder``.
    :param safe: Controls if only ``dict`` objects may be serialized. Defaults
      to ``True``.
    """

    def __init__(self, data, encoder=DjangoJSONEncoder, safe=True, **kwargs):
        if safe and not isinstance(data, dict):
            raise TypeError('In order to allow non-dict objects to be '
                            'serialized set the safe parameter to False')
        kwargs.setdefault('content_type', 'application/json')
        data = json.dumps(data, cls=encoder)
        super(JsonResponse, self).__init__(content=data, **kwargs)


def get_app_list(context, order=True):
    admin_site = get_admin_site(context)
    request = context['request']

    app_dict = {}
    for model, model_admin in admin_site._registry.items():

        app_icon = model._meta.app_config.icon if hasattr(model._meta.app_config, 'icon') else None
        app_label = model._meta.app_label
        try:
            has_module_perms = model_admin.has_module_permission(request)
        except AttributeError:
            has_module_perms = request.user.has_module_perms(app_label)  # Fix Django < 1.8 issue

        if has_module_perms:
            perms = model_admin.get_model_perms(request)

            # Check whether user has any perm for this module.
            # If so, add the module to the model_list.
            if True in perms.values():
                info = (app_label, model._meta.model_name)
                model_dict = {
                    'name': capfirst(model._meta.verbose_name_plural),
                    'object_name': model._meta.object_name,
                    'perms': perms,
                    'model_name': model._meta.model_name
                }
                if perms.get('change', False) or perms.get("view", False):
                    try:
                        model_dict['admin_url'] = reverse('admin:%s_%s_changelist' % info, current_app=admin_site.name)
                    except NoReverseMatch:
                        pass
                if perms.get('add', False):
                    try:
                        model_dict['add_url'] = reverse('admin:%s_%s_add' % info, current_app=admin_site.name)
                    except NoReverseMatch:
                        pass
                if app_label in app_dict:
                    app_dict[app_label]['models'].append(model_dict)
                else:
                    try:
                        name = apps.get_app_config(app_label).verbose_name
                    except NameError:
                        name = app_label.title()
                    app_dict[app_label] = {
                        'name': name,
                        'app_label': app_label,
                        'app_url': reverse(
                            'admin:app_list',
                            kwargs={'app_label': app_label},
                            current_app=admin_site.name,
                        ),
                        'has_module_perms': has_module_perms,
                        'models': [model_dict],
                    }

                if not app_icon:
                    app_icon = default_apps_icon[app_label] if app_label in default_apps_icon else None
                app_dict[app_label]['icon'] = app_icon

    # Sort the apps alphabetically.
    app_list = list(app_dict.values())

    if order:
        app_list.sort(key=lambda x: x['name'].lower())

        # Sort the models alphabetically within each app.
        for app in app_list:
            app['models'].sort(key=lambda x: x['name'])

    return app_list


def get_admin_site(context):
    try:
        current_resolver = resolve(context.get('request').path)
        index_resolver = resolve(reverse('%s:index' % current_resolver.namespaces[0]))

        if hasattr(index_resolver.func, 'admin_site'):
            return index_resolver.func.admin_site

        for func_closure in index_resolver.func.__closure__:
            if isinstance(func_closure.cell_contents, AdminSite):
                return func_closure.cell_contents
    except:
        pass

    return admin.site


def get_admin_site_name(context):
    return get_admin_site(context).name


class SuccessMessageMixin(object):
    """
    Adds a success message on successful form submission.
    """
    success_message = ''

    def form_valid(self, form):
        response = super(SuccessMessageMixin, self).form_valid(form)
        success_message = self.get_success_message(form.cleaned_data)
        if success_message:
            messages.success(self.request, success_message)
        return response

    def get_success_message(self, cleaned_data):
        return self.success_message % cleaned_data


def get_model_queryset(admin_site, model, request, preserved_filters=None):
    model_admin = admin_site._registry.get(model)

    if model_admin is None:
        return

    try:
        changelist_url = reverse('%s:%s_%s_changelist' % (
            admin_site.name,
            model._meta.app_label,
            model._meta.model_name
        ))
    except NoReverseMatch:
        return

    changelist_filters = None

    if preserved_filters:
        changelist_filters = preserved_filters.get('_changelist_filters')

    if changelist_filters:
        changelist_url += '?' + changelist_filters

    if model_admin:
        queryset = model_admin.get_queryset(request)
    else:
        queryset = model.objects

    list_display = model_admin.get_list_display(request)
    list_display_links = model_admin.get_list_display_links(request, list_display)
    list_filter = model_admin.get_list_filter(request)
    search_fields = model_admin.get_search_fields(request) \
        if hasattr(model_admin, 'get_search_fields') else model_admin.search_fields
    list_select_related = model_admin.get_list_select_related(request) \
        if hasattr(model_admin, 'get_list_select_related') else model_admin.list_select_related

    actions = model_admin.get_actions(request)
    if actions:
        list_display = ['action_checkbox'] + list(list_display)

    ChangeList = model_admin.get_changelist(request)

    change_list_args = [
        request, model, list_display, list_display_links, list_filter,
        model_admin.date_hierarchy, search_fields, list_select_related,
        model_admin.list_per_page, model_admin.list_max_show_all,
        model_admin.list_editable, model_admin]

    try:
        sortable_by = model_admin.get_sortable_by(request)
        change_list_args.append(sortable_by)
    except AttributeError:
        # django version < 2.1
        pass

    try:
        cl = ChangeList(*change_list_args)
        queryset = cl.get_queryset(request)
    except IncorrectLookupParameters:
        pass

    return queryset


def get_possible_language_codes():
    language_code = translation.get_language()

    language_code = language_code.replace('_', '-').lower()
    language_codes = []

    # making dialect part uppercase
    split = language_code.split('-', 2)
    if len(split) == 2:
        language_code = '%s-%s' % (split[0].lower(), split[1].upper()) if split[0] != split[1] else split[0]

    language_codes.append(language_code)

    # adding language code without dialect part
    if len(split) == 2:
        language_codes.append(split[0].lower())

    return language_codes


def get_original_menu_items(context):
    if context.get('user') and user_is_authenticated(context['user']):
        # pinned_apps = PinnedApplication.objects.filter(user=context['user'].pk).values_list('app_label', flat=True)
        pinned_apps = []
    else:
        pinned_apps = []

    original_app_list = get_app_list(context)

    return map(lambda app: {
        'app_label': app['app_label'],
        'url': app['app_url'],
        'url_blank': False,
        'label': app.get('name', capfirst(_(app['app_label']))),
        'has_perms': app.get('has_module_perms', False),
        'icon': app.get('icon', None),
        'models': list(map(lambda model: {
            'url': model.get('admin_url'),
            'url_blank': False,
            'name': model['model_name'],
            'object_name': model['object_name'],
            'label': model.get('name', model['object_name']),
            'has_perms': any(model.get('perms', {}).values()),
        }, app['models'])),
        'pinned': app['app_label'] in pinned_apps,
        'custom': False
    }, original_app_list)


def get_menu_item_url(url, original_app_list):
    if isinstance(url, dict):
        url_type = url.get('type')

        if url_type == 'app':
            return original_app_list[url['app_label']]['url']
        elif url_type == 'model':
            models = dict(map(
                lambda x: (x['name'], x['url']),
                original_app_list[url['app_label']]['models']
            ))
            return models[url['model']]
        elif url_type == 'reverse':
            return reverse(url['name'], args=url.get('args'), kwargs=url.get('kwargs'))
    elif isinstance(url, str):
        return url


def get_menu_items(context):
    """
    Return a list of menu items for the admin interface
    """
    request = context.get('request')
    if not request or not request.user.is_authenticated:
        return []

    menu_items = []

    # Add Logistics section
    if request.user.groups.filter(name__in=['Viewer', 'Uploader']).exists() or request.user.is_superuser:
        logistics_items = []
        
        # Master Waybill List (visible to both Viewer and Uploader)
        logistics_items.append({
            'name': 'Master Waybill List',
            'url': reverse('admin:logistics_masterwaybill_changelist'),
            'icon': 'fas fa-list'
        })
        
        # Waybills (visible to both Viewer and Uploader)
        logistics_items.append({
            'name': 'Waybills',
            'url': reverse('admin:logistics_waybill_changelist'),
            'icon': 'fas fa-file-alt'
        })
        
        # Warehouse Receipts (visible to both Viewer and Uploader)
        logistics_items.append({
            'name': 'Warehouse Receipts',
            'url': reverse('admin:logistics_warehousereceipt_changelist'),
            'icon': 'fas fa-warehouse'
        })
        
        # Excel Upload (visible only to Uploader)
        if request.user.groups.filter(name='Uploader').exists() or request.user.is_superuser:
            logistics_items.append({
                'name': 'Upload Excel',
                'url': reverse('admin:logistics_excelupload_changelist'),
                'icon': 'fas fa-file-excel'
            })
        
        menu_items.append({
            'name': 'Logistics',
            'icon': 'fas fa-truck',
            'items': logistics_items
        })

    # Add User Management section for superusers
    if request.user.is_superuser:
        menu_items.append({
            'name': 'User Management',
            'icon': 'fas fa-users',
            'items': [
                {
                    'name': 'Users',
                    'url': reverse('admin:auth_user_changelist'),
                    'icon': 'fas fa-user'
                },
                {
                    'name': 'Groups',
                    'url': reverse('admin:auth_group_changelist'),
                    'icon': 'fas fa-users-cog'
                }
            ]
        })

    return menu_items


def context_to_dict(context):
    if isinstance(context, Context):
        flat = {}
        for d in context.dicts:
            flat.update(d)
        context = flat

    return context


def user_is_authenticated(user):
    if not hasattr(user.is_authenticated, '__call__'):
        return user.is_authenticated
    else:
        return user.is_authenticated()
