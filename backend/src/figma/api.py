from rest_framework.views import APIView, Response
import requests
import re
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from .serializers import OpenAIHTMLSerializer
from .models import *
from .clients.openai_client import OpenAIClient
from rest_framework.permissions import IsAuthenticated


OPENAI_API_KEY = settings.OPENAI_API_KEY
openai_client = OpenAIClient(OPENAI_API_KEY)

class OpenAIHTMLAPIView(APIView):
    _SERVICE_NAME  = "OpenAIClient"
    permission_classes = [IsAuthenticated]  


    @swagger_auto_schema(request_body=OpenAIHTMLSerializer)
    def post(self, request, *args, **kwargs):

        serializer = OpenAIHTMLSerializer(data=request.data)
        if serializer.is_valid():
            text_description = serializer.validated_data.get("text_description")
        else:
            return Response(serializer.errors, status=400)

        response = openai_client.generate_html(text_description) 

        try:

            api_service = Service.objects.get(service_name=self._SERVICE_NAME) 
        except Service.DoesNotExist:
            return Response({"error": f"Service with name {api_service_name} does not exist."}, status=400)

       # Create a new UserApiInteractionHistory object
        user_interaction = UserApiInteractionHistory(

            user=request.user,  
            user_prompt=text_description,
            api_service=api_service,
            api_output=""  # Initially empty; will be filled later
           
        )

        if response.status_code == 200:
            body_content = response.json().get('choices')[0].get('text').strip()
            if re.search(r'<div id="container">', body_content, re.IGNORECASE):
                full_html = f"""
                                <!DOCTYPE html>
                                <html lang="en">
                                <head>
                                    <meta charset="UTF-8">
                                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                                    <script src="https://cdn.tailwindcss.com"></script>
                                </head>
                                <body>
                                    {body_content}
                                </body>
                                </html>
                                """
                user_interaction.api_output = full_html
                try:
                    user_interaction.save()
                except Exception as e:
                    # Log the error for debugging
                    # Consider using a logging system like CloudWatch

                    # Didn't return the error to frontend (client) because response request was already 200
                    # Problem was coming from user_interaction model
                    pass    

                return Response({"html_code": full_html}, status=200)
                
            else:
                return Response({"error": "The response did not contain recognizable HTML code within a div#container."}, status=400)
        else:
            return Response({"error": f"Error calling OpenAI API: {response.status_code}"}, status=400)
        
    def get(self, request, *args, **kwargs):
        # This is a simple GET request for testing purposes
        return Response({"message": "GET request to OpenAIHTMLAPIView is successful."}, status=200)