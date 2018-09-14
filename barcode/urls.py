from django.urls import path
from barcode.views import *


urlpatterns = [
    path('api/barcode',
         BarcodeReaderAPI.as_view()),
]
