from django.urls import path
from .views import ShortUrlCreateView, ShortUrlResolveView

urlpatterns = [
    path("shrt/", ShortUrlCreateView.as_view()),
    path("shrt/<str:code>/", ShortUrlResolveView.as_view()),
]