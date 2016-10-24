from .models import Batch
from rest_framework import serializers

class BatchSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Batch
        fields = ('id', 'text')
    # = serializers.Field(source='popularity')
