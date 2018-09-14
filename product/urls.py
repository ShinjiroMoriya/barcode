from django.urls import path
from product.views import *


urlpatterns = [
    path('admin/products', ProductsView.as_view()),
    path('admin/products/<int:product_id>', ProductView.as_view()),
    path('admin/products/<int:product_id>/delete', ProductsDeleteView.as_view()),
    path('admin/products/create', ProductsCreateView.as_view()),
    path('admin/categories', CategoriesView.as_view()),
    path('admin/categories/<int:category_id>', CategoryView.as_view()),
    path('admin/categories/<int:category_id>/delete', CategoryDeleteView.as_view()),
    path('admin/categories/create', CategoriesCreateView.as_view()),
]
