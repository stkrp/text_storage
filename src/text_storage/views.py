from django.views.generic import TemplateView
from rest_framework.generics import ListCreateAPIView

from .models import Text
from .pagination import NumericPageNumberPagination
from .serializers import TextSerializer


class TextListAPIView(ListCreateAPIView):
    # T. к. по требованиям не нужно создавать `DetailView`, то для
    # сохранения возможности просмотреть отправленный текст целиком, в списке
    # отображаются полные тексты, а не срезы.
    queryset = Text.objects.order_by('-created_at', '-id')
    serializer_class = TextSerializer
    pagination_class = NumericPageNumberPagination


class TextListView(TemplateView):
    template_name = 'text_storage/text_list.html'
