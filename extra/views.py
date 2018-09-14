import base64
import zbarlight
from django.core.files.base import ContentFile
from django.views import View
from django.template.response import TemplateResponse
from product.models import Product
from barcode_app.services import image_uploader


class TopView(View):
    @staticmethod
    def get(request):
        return TemplateResponse(request, 'index.html', {
            'barcodes': [],
            'products': [],
        })

    @staticmethod
    def post(request):
        barcodes = []
        products = []

        try:
            data = request.POST.get('barcode_base64')
            img_format, img_str = data.split(';base64,')
            image = ContentFile(base64.b64decode(img_str))
            image = image_uploader(image)
            codes = zbarlight.scan_codes(['ean13'], image)
            if codes is not None:
                barcodes = [d.decode('utf-8') for d in codes]
                products = Product.get_by_barcodes(barcodes)

        except Exception as e:
            print('Exception', str(e))

        return TemplateResponse(request, 'index.html', {
            'barcodes': barcodes,
            'products': products,
        })
