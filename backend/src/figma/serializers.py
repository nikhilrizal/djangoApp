from rest_framework import serializers

class OpenAIHTMLSerializer(serializers.Serializer):
    text_description = serializers.CharField(help_text="Description of the HTML content to generate.")
