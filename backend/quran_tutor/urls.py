"""
URL configuration for quran_tutor project.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('', TemplateView.as_view(template_name='index.html'), name='webapp_home'),
    path('app/', TemplateView.as_view(template_name='index.html'), name='webapp'),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^(?P<path>(css|js|images|audio|assets)/.*)$', serve, {'document_root': settings.STATICFILES_DIRS[0]}),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

