import tempfile
from django.views import View
from django.http import JsonResponse
import zbarlight
from PIL import Image
from django.conf import settings
from barcode_app.services import image_uploader
from product.models import Product
from product.serializers import ProductSerializer


class BarcodeReaderAPI(View):
    @staticmethod
    def post(request):
        try:
            image = image_uploader(request.FILES.get('barcode'))
            codes = zbarlight.scan_codes(['ean13'], image)

            if codes is None:
                return JsonResponse({
                    'barcodes': [],
                    'products': [],
                    'message': 'バーコードが認識できませんでした。'
                }, status=404)

            barcodes = [d.decode('utf-8') for d in codes]

            products = Product.get_by_barcodes(barcodes)

            if products is None:
                return JsonResponse({
                    'barcodes': barcodes,
                    'products': [],
                    'message': '該当する商品がありません。'
                }, status=404)

            return JsonResponse({
                'barcodes': barcodes,
                'products': ProductSerializer(products, many=True).data
            })

        except Exception as e:
            print('Exception', str(e))

            return JsonResponse({
                'barcodes': [],
                'products': [],
                'message': str(e)
            })
