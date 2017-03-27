from rest_framework.serializers import ModelSerializer

from .models import Text


class TextSerializer(ModelSerializer):
    class Meta:
        model = Text
        fields = '__all__'
