from django.urls import path, re_path, include
from django.conf import settings
from django.views.generic import TemplateView

urlpatterns = [
    path('', include('extra.urls')),
    path('', include('barcode.urls')),
    path('', include('product.urls')),
    path('favicon.ico', TemplateView.as_view(template_name='favicon.ico')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += re_path(r'^__debug__/', include(debug_toolbar.urls)),
