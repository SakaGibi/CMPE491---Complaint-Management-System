from rest_framework import serializers
from .models import SuggestionOrComplaint

class SuggestionOrComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = SuggestionOrComplaint
        fields = '__all__'