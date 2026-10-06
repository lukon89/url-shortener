from rest_framework import serializers

class UrlShortenerSerializer(serializers.Serializer):
    url = serializers.URLField()