from rest_framework import serializers


class SupportSerializer(serializers.Serializer):
    subject = serializers.CharField(max_length=255)
    message = serializers.CharField(max_length=1000)
