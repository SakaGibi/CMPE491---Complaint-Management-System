from rest_framework import serializers
from .models import SupportMessage

class SupportMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportMessage
        fields = '__all__'