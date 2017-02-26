from .models import Batch, Currency
from rest_framework import serializers

class BatchSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Batch
        fields = ('id', 'text', 'price')
    # = serializers.Field(source='popularity')

class CurrencySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Currency
        fields = ('id', 'conversion_rate')
    # = serializers.Field(source='popularity')
