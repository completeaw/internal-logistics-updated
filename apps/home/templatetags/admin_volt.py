# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import re
from django import template
from django.utils.html import format_html
from django.contrib.admin.sites import site
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.contrib.auth.models import User
from django.contrib.admin.views.main import (PAGE_VAR)

register = template.Library()
assignment_tag = register.assignment_tag if hasattr(register, 'assignment_tag') else register.simple_tag

from apps.home.utils import get_menu_items


@register.filter
def clean_text(value):
    res = value.replace('\n', ' ')
    return res


@register.filter
def checkbox(value):
    res = re.sub(r"</?(?i:td)(.|\n)*?>", "", value)
    return res


@register.simple_tag(takes_context=True)
def admin_get_menu(context):
    """
    Return the admin menu items with proper permissions
    """
    return get_menu_items(context)


@register.simple_tag(takes_context=True)
def admin_get_menu_item_url(context, item):
    """
    Return the URL for a menu item
    """
    if 'url' in item:
        return item['url']
    return '#'


@register.filter
def admin_get_item_icon(item):
    """
    Return the icon class for a menu item
    """
    return item.get('icon', 'fas fa-circle')


@assignment_tag(takes_context=True)
def get_direction(context):
    res = {
        'panel': 'text-left',
        'notify': 'right',
        'float': 'float-right',
        'reverse_panel': 'text-right',
        'nav': 'ml-auto'
    }

    if context.get('LANGUAGE_BIDI'):
        res['panel'] = 'text-right'
        res['notify'] = 'left'
        res['float'] = ''
        res['reverse_panel'] = 'text-left'
        res['nav'] = 'mr-auto'
    return res


@assignment_tag(takes_context=True)
def get_admin_setting(context):
    # user = context.get('request').user
    # admin_black_setting = user.admin_black_setting if hasattr(user, 'admin_black_setting') else None
    res = {
        # 'sidebar_background': admin_black_setting.sidebar_background if admin_black_setting else 'primary',
        # 'dark_mode': admin_black_setting.dark_mode if admin_black_setting else True,
        # 'input_bg_color': '#ffffff' if admin_black_setting and not admin_black_setting.dark_mode else '#27293c'
    }

    return res


@register.simple_tag
def paginator_number(cl, i):
    """
    Generate an individual page index link in a paginated list.
    """
    if i == cl.paginator.ELLIPSIS:
        return format_html('{} ', cl.paginator.ELLIPSIS)
    elif i == cl.page_num:
        return format_html('<a href="" class="page-link">{}</a> ', i)
    else:
        return format_html(
            '<a href="{}" class="page-link {}">{}</a> ',
            cl.get_query_string({PAGE_VAR: i}),
            mark_safe('end' if i == cl.paginator.num_pages else ''),
            i,
        )


@register.filter
def sum_number(value, number):
    return value + number


@register.filter
def neg_num(value, number):
    return value - number
