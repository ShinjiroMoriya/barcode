from django.views import View
from product.forms import ProductForm, CategoryForm, CSVUploadForm
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.contrib import messages
from barcode_app.services import get_error_message
from product.models import Product, ProductCategory
from io import TextIOWrapper
import csv


class ProductsView(View):
    @staticmethod
    def get(request):
        products = Product.get_all()
        return TemplateResponse(request, 'products.html', {
            'products': products,
            'error_messages': {}
        })

    @staticmethod
    def post(request):

        form = CSVUploadForm(request.POST, request.FILES)

        if form.errors:
            messages.add_message(request, messages.INFO,
                                 dict(form.errors.items()))

        if form.is_valid():

            form_data = TextIOWrapper(form.cleaned_data.get('csv'), encoding='utf-8')
            try:
                csv_file = csv.reader(form_data)
                next(csv_file)
                add_product = []
                for c in csv_file:
                    already_product = Product.get_by_jan_code(c[4])
                    if already_product is None:
                        add_product.append(Product(
                            product_name=c[1],
                            brand=c[0],
                            model_number=c[2],
                            category=ProductCategory.get_by_name(c[3]),
                            jan_code=c[4],
                        ))

                Product.objects.bulk_create(add_product)

            except:
                products = Product.get_all()
                return TemplateResponse(request, 'products.html', {
                    'products': products,
                    'error_messages': get_error_message(request),
                })

        return HttpResponseRedirect('/admin/products')


class ProductsCreateView(View):
    @staticmethod
    def get(request):
        categories = ProductCategory.get_all()
        return TemplateResponse(request, 'products_create.html', {
            'categories': categories,
            'error_messages': {},
            'form_data': {},
        })
        
    @staticmethod
    def post(request):
    
        form = ProductForm(request.POST)

        if form.errors:
            messages.add_message(request, messages.INFO,
                                 dict(form.errors.items()))

        if form.is_valid():
            try:
                Product.create_product({
                    'brand': form.cleaned_data.get('brand'),
                    'product_name': form.cleaned_data.get('product_name'),
                    'model_number': form.cleaned_data.get('model_number'),
                    'category': ProductCategory.get_by_id(
                        form.cleaned_data.get('category')),
                    'jan_code': form.cleaned_data.get('jan_code'),
                })
            
                return HttpResponseRedirect('/admin/products')

        
            except:
                pass

        categories = ProductCategory.get_all()
        return TemplateResponse(
            request, 'products_create.html', {
                'categories': categories,
                'form_data': form.cleaned_data,
                'error_messages': get_error_message(request),
            })


class ProductView(View):
    @staticmethod
    def get(request, product_id):
        product = Product.get_by_id(product_id)
        categories = ProductCategory.get_all()
        return TemplateResponse(request, 'product.html', {
            'product': product,
            'categories': categories,
            'error_messages': {},
            'form_data': {},
        })

    @staticmethod
    def post(request, product_id):

        form = ProductForm(request.POST)

        if form.errors:
            messages.add_message(request, messages.INFO,
                                 dict(form.errors.items()))

        if form.is_valid():
            try:
                Product.edit_product(product_id, {
                    'brand': form.cleaned_data.get('brand'),
                    'product_name': form.cleaned_data.get('product_name'),
                    'model_number': form.cleaned_data.get('model_number'),
                    'category': ProductCategory.get_by_id(
                        form.cleaned_data.get('category')),
                    'jan_code': form.cleaned_data.get('jan_code'),
                })

                return HttpResponseRedirect('/admin/products')

            except:
                pass

        categories = ProductCategory.get_all()
        return TemplateResponse(
            request, 'products_create.html', {
                'categories': categories,
                'form_data': form.cleaned_data,
                'error_messages': get_error_message(request),
            })


class ProductsDeleteView(View):
    @staticmethod
    def post(_, product_id):
        product = Product.get_by_id(product_id)
        if product is None:
            return HttpResponseRedirect('/admin/products')

        try:
            Product.delete_product(product_id)
            return HttpResponseRedirect('/admin/products')

        except:
            return HttpResponseRedirect('/admin/products/' + product_id)


class CategoriesView(View):
    @staticmethod
    def get(request):
        categories = ProductCategory.get_all()
        return TemplateResponse(request, 'categories.html', {
            'categories': categories,
        })


class CategoriesCreateView(View):
    @staticmethod
    def get(request):
        return TemplateResponse(request, 'categories_create.html', {
            'error_messages': {},
            'form_data': {},
        })

    @staticmethod
    def post(request):

        form = CategoryForm(request.POST)

        if form.errors:
            messages.add_message(request, messages.INFO,
                                 dict(form.errors.items()))

        if form.is_valid():
            try:
                ProductCategory.create_category({
                    'name': form.cleaned_data.get('name'),
                })
                return HttpResponseRedirect('/admin/categories')

            except:
                pass

        return TemplateResponse(
            request, 'categories_create.html', {
                'form_data': form.cleaned_data,
                'error_messages': get_error_message(request),
            })


class CategoryView(View):
    @staticmethod
    def get(request, category_id):
        category = ProductCategory.get_by_id(category_id)
        product_use = Product.get_by_category_id(category_id)
        return TemplateResponse(request, 'category.html', {
            'category': category,
            'product_use': len(product_use) != 0,
            'error_messages': {},
            'form_data': {},
        })

    @staticmethod
    def post(request, category_id):

        form = CategoryForm(request.POST)

        if form.errors:
            messages.add_message(request, messages.INFO,
                                 dict(form.errors.items()))

        if form.is_valid():
            try:
                ProductCategory.edit_category(category_id, {
                    'name': form.cleaned_data.get('name'),
                })
                return HttpResponseRedirect('/admin/categories')

            except:
                pass

        category = ProductCategory.get_by_id(category_id)
        return TemplateResponse(
            request, 'category.html', {
                'category': category,
                'form_data': form.cleaned_data,
                'error_messages': get_error_message(request),
            })


class CategoryDeleteView(View):
    @staticmethod
    def post(request, category_id):
        category = ProductCategory.get_by_id(category_id)
        if category is None:
            return HttpResponseRedirect('/admin/categories')

        product_use = Product.get_by_category_id(category_id)
        if product_use is not None:
            return TemplateResponse(
                request, 'category.html', {
                    'category': category,
                    'form_data': {},
                    'error_messages': '利用しているカテゴリーです。',
                })

        try:
            ProductCategory.delete_category(category_id)
            return HttpResponseRedirect('/admin/categories')

        except:
            return HttpResponseRedirect('/admin/categories/' + category_id)
