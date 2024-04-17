# from rest_framework.views import APIView, Response
# import requests
# import re
# from django.conf import settings
# from drf_yasg.utils import swagger_auto_schema
from .serializers import OpenAIHTMLSerializer
# import json

# OPENAI_API_KEY = settings.OPENAI_API_KEY
# OPENROUTER_API_KEY=settings.OPENROUTER_API_KEY
# class OpenAIHTMLAPIView(APIView):

#     @swagger_auto_schema(request_body=OpenAIHTMLSerializer)
#     def post(self, request, *args, **kwargs):
#         serializer = OpenAIHTMLSerializer(data=request.data)
#         if serializer.is_valid():
#             text_description = serializer.validated_data.get("text_description")
#         else:
#             return Response(serializer.errors, status=400)
#         openai_api_key = OPENAI_API_KEY

#         #prompt = f"Directly provide full HTML code for the body of a {text_description},follow the text instruction strictly and add each and every element mentioned in text description, use Tailwind CSS classes for styling, style page keeping in view user experience and make it eye catching. Include CSS animations for dynamic effects. HTML code only, no additional text or explanations. Wrap the content in a div with an id of 'container' also close that tag."
#         prompt = f"""
#             Design a web component as per the following specifications:

#             1. Wrap the entire content in a <div> element with an id of 'container' and close the tag appropriately.

#             2. Utilize HTML and apply Tailwind CSS classes for styling.

#             3. Ensure that every element mentioned in the text description is included in the design.

#             4. Pay attention to user experience and make the design visually appealing.

#             5. Incorporate CSS animations for dynamic effects.

#             Text Description:
#             {text_description}

#             Strictly generate the HTML code for the web component based on the provided text description. Ensure that the design adjusts dynamically according to the specified page requirements. Do not include any additional text or explanations, only the HTML code.
#             """

#         response = requests.post(
#             "https://api.openai.com/v1/completions",
#             headers={
#                 "Authorization": f"Bearer {openai_api_key}",
#                 "Content-Type": "application/json"
#             },
#             json={
#                 "model": "gpt-3.5-turbo-instruct",
#                 "prompt": prompt,
#                 "temperature": 0.3,
#                 "max_tokens": 1024,
#                 "top_p": 1.0,
#                 "frequency_penalty": 0.0,
#                 "presence_penalty": 0.0,
#                 "stop": ["</div>"]
#             }
#         )
#         # response = requests.post(
#         # url="https://openrouter.ai/api/v1/chat/completions",
#         # headers={
#         #     "Authorization": f"Bearer {OPENROUTER_API_KEY}",
#         #     # "HTTP-Referer": f"{YOUR_SITE_URL}", # Optional, for including your app on openrouter.ai rankings.
#         #     # "X-Title": f"{YOUR_APP_NAME}", # Optional. Shows in rankings on openrouter.ai.
#         # },
#         # data=json.dumps({
#         #     "model": "openrouter/auto", # Optional
#         #     "messages": prompt
#         # })
#         # )

#         if response.status_code == 200:
#             body_content = response.json().get('choices')[0].get('text').strip()
#             if re.search(r'<div id="container">', body_content, re.IGNORECASE):
#                 full_html = f"""
# <!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <script src="https://cdn.tailwindcss.com"></script>
# </head>
# <body>
# <div id="container">
#     {body_content}
# </body>
# </html>
# """
#                 return Response({"html_code": full_html}, status=200)
#             else:
#                 return Response({"error": "The response did not contain recognizable HTML code within a div#container."}, status=400)
#         else:
#             return Response({"error": f"Error calling OpenAI API: {response.status_code}"}, status=400)
        
    # def get(self, request, *args, **kwargs):
    # # This is a simple GET request for testing purposes
    #     return Response({"message": "GET request to OpenAIHTMLAPIView is successful."}, status=200)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
from .models import *
import json
from rest_framework.permissions import IsAuthenticated


class OpenAIHTMLAPIView(APIView):
    
    
    BASE_PROMPT = """
        Design a web component using HTML and apply Tailwind CSS classes for styling.
        
        Strictly generate the HTML code for the web component. Ensure that the design adjusts dynamically according to the specified page requirements. 
        """

    _SERVICE_NAME  = "openrouter"
    permission_classes = [IsAuthenticated]
    def extract_html_code(self, text_prompt):
        OPENROUTER_API_KEY = "sk"  # Replace with your API key

        full_text_prompt = f"{self.BASE_PROMPT}\n{text_prompt}"

        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            },
            data=json.dumps({
                "model": "openrouter/auto",
                "messages": [
                    {"role": "user", "content": full_text_prompt}
                ]
            })
        )

        if response.status_code == 200:
            data = response.json()
            html_content = ""
            for choice in data.get('choices', []):
                if 'message' in choice and 'content' in choice['message']:
                    html_content += choice['message']['content']
            # Extract content enclosed within triple backticks
            start_index = html_content.find('```html') + 7
            end_index = html_content.find('```', start_index)
            html_code = html_content[start_index:end_index].strip()  # Strip whitespace
            # Ensure the first div in body has id="container"
            if '<div' in html_code:
                html_code = html_code.replace('<div', '<div id="container"', 1)
            return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<div id="container">
<body>
    {html_code}
</div>
</body>
</html>"""
        else:
            return f"Error: {response.status_code} - {response.text}"
    
    def post(self, request, *args, **kwargs):
        

        try:
            api_service = Service.objects.get(service_name=self._SERVICE_NAME) 
        except Service.DoesNotExist:
            return Response({"error": f"Service with name {api_service_name} does not exist."}, status=503)
        
        # Create a new UserApiInteractionHistory object
        user_interaction = UserApiInteractionHistory(

            user=request.user,  
            user_prompt=text_description,
            api_service=api_service,
            api_output=""  # Initially empty; will be filled later
           
        )

        serializer = OpenAIHTMLSerializer(data=request.data)
        if serializer.is_valid():
            text_description = serializer.validated_data.get("text_description")
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the HTML code based on the text prompt
        html_code = self.extract_html_code(text_description)
        user_interaction.api_output = full_html
        try:
            user_interaction.save()
        except Exception as e:
            # Log the error for debugging
            # Consider using a logging system like CloudWatch 
            #  Didn't return the error to frontend (client) because response request was already 200
            # Problem was coming from user_interaction model
            pass    


        return Response({"html_code": html_code}, status=status.HTTP_200_OK)
