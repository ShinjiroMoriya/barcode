from django import forms
from barcode_app.validator import ERROR_MESSAGES
from product.models import ProductCategory


class ProductForm(forms.Form):
    brand = forms.CharField(required=True,
                            error_messages=ERROR_MESSAGES, )
    product_name = forms.CharField(required=True,
                                   error_messages=ERROR_MESSAGES, )
    model_number = forms.CharField(required=True,
                                   error_messages=ERROR_MESSAGES, )
    jan_code = forms.CharField(required=True,
                               error_messages=ERROR_MESSAGES, )
    category = forms.ChoiceField(
        required=True,
        widget=forms.Select,
        choices=lambda: [(v.id, v.id) for v in ProductCategory.get_all()],
        error_messages = ERROR_MESSAGES, )


class CategoryForm(forms.Form):
    name = forms.CharField(required=True,
                           error_messages=ERROR_MESSAGES, )
