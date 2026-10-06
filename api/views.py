import logging
import random
import string

from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request


from .serializers import UrlShortenerSerializer
from .db import urls_storage

logger = logging.getLogger(__name__)


def generate_unique_code() -> str:
    chars = string.ascii_letters + string.digits
    while True:
        code = ''.join(random.choices(chars, k=6))
        if code not in urls_storage:
            return code


class ShortUrlCreateView(APIView):

    def post(self, request: Request) -> Response:
        serializer = UrlShortenerSerializer(data=request.data)
        if not serializer.is_valid():
            logger.error("Invalid payload", extra={"errors": serializer.errors})
            return Response(serializer.errors)
        
        code = generate_unique_code()
        long_url = serializer.validated_data["url"]
        urls_storage[code] = serializer.validated_data["url"]
        logger.info(f"Code {code} generated for long url {long_url}")
        return Response({"short_url": request.build_absolute_uri(f'/shrt/{code}')})
    

class ShortUrlResolveView(APIView):

    def get(self, request: Request, code: str) -> Response:
        long_url = urls_storage.get(code)
        if not long_url:
            return Response({"error": "Not found"}, status=404)
        
        logger.info(f"Long url {long_url} found for code {code}")
        return Response({"original_url": long_url})
