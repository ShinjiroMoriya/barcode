from django.views import View
from django.template.response import TemplateResponse


class TopView(View):
    @staticmethod
    def get(request):
        return TemplateResponse(request, 'index.html', {})
