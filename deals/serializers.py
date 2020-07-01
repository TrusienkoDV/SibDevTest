from rest_framework import serializers
from deals.models import Deal


class DealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deal
        exclude = ['id']
