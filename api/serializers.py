from rest_framework import serializers


class ShortenUrlSerializer(serializers.Serializer):
    url = serializers.URLField()


class ShortUrlCreateResponseSerializer(serializers.Serializer):
    short_url = serializers.URLField()


class ShortUrlResolveResponseSerializer(serializers.Serializer):
    long_url = serializers.URLField()