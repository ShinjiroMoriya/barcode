from django.views import View
from django.http import JsonResponse
import zbarlight
from barcode_app.services import image_uploader
from product.models import Product
from product.serializers import ProductSerializer
import base64
from django.core.files.base import ContentFile


class BarcodeReaderAPI(View):
    @staticmethod
    def post(request):
        try:
            data = request.POST.get('barcode')
            img_format, img_str = data.split(';base64,')
            image = ContentFile(base64.b64decode(img_str))
            image = image_uploader(image)
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
