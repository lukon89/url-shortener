import logging
import random
import string

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request


from .serializers import ShortenUrlSerializer, ShortUrlCreateResponseSerializer, ShortUrlResolveResponseSerializer
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
        serializer = ShortenUrlSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning("Invalid payload", extra={"errors": serializer.errors})
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        code = generate_unique_code()
        long_url = serializer.validated_data["url"]
        urls_storage[code] = long_url
        logger.info(f"Code {code} generated for long url {long_url}")
        response = ShortUrlCreateResponseSerializer(data={"short_url": request.build_absolute_uri(f'/shrt/{code}')})
        if not response.is_valid():
            logger.error("Invalid response data", extra={"errors": response.errors})
            return Response({"error": "Internal error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(response.data)
    

class ShortUrlResolveView(APIView):

    def get(self, request: Request, code: str) -> Response:
        long_url = urls_storage.get(code)
        if not long_url:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        logger.info(f"Long url {long_url} found for code {code}")
        response = ShortUrlResolveResponseSerializer(data={"long_url": long_url})
        if not response.is_valid():
            logger.error("Corrupted data in storage", extra={"code": code, "errors": response.errors})
            return Response({"error": "Internal error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(response.data)
