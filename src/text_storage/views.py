from rest_framework.generics import ListCreateAPIView

from .models import Text
from .serializers import TextSerializer


class TextListView(ListCreateAPIView):
    # T. к. по требованиям не нужно создавать `DetailView`, то для
    # сохранения возможности просмотреть отправленный текст целиком, в списке
    # отображаются полные тексты, а не срезы.
    queryset = Text.objects.order_by('-created_at', '-id')
    serializer_class = TextSerializer
