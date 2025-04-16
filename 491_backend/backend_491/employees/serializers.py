from rest_framework import serializers

class EmployeeLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
