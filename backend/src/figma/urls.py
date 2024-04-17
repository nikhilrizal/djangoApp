from django.urls import path

from django.conf import settings

from . import api

urlpatterns = [
    path("openai-html/", api.OpenAIHTMLAPIView.as_view(), name="openai-html"),    
]
