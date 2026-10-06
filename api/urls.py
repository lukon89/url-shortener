from django.urls import path, include
from .views import HelloView

urlpatterns = [path("hello/", HelloView.as_view())]