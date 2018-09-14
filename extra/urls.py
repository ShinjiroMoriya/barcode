from django.urls import path
from extra.views import *


urlpatterns = [
    path('', TopView.as_view()),
]
