"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from apps.home import views
from django.views.static import serve

handler404 = 'apps.home.views.handler404'
handler403 = 'apps.home.views.handler403'
handler500 = 'apps.home.views.handler500'

urlpatterns = [
    path('admin/', include('apps.logistics.urls_admin')),  # Use our custom admin site
    path('', include('apps.home.urls')),  # Use home app as the main landing page
    path('logistics/', include('apps.logistics.urls')),
    path('file-manager/', include('apps.file_manager.urls')),
    path('tables/', include('apps.tables.urls')),
    path("api/", include("apps.api.urls")),
    path('accounts/', include('allauth.urls')),
    path('tasks/', include('apps.tasks.urls')),
    path('charts/', include('apps.charts.urls')),
    path("users/", include("apps.users.urls")),
    path('i18n/', include('django.conf.urls.i18n')),

    re_path(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}), 
    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}), 
    
    # Debug toolbar
    path("__debug__/", include("debug_toolbar.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


urlpatterns += i18n_patterns(
    path('i18n/', views.i18n_view, name="i18n_view")
)