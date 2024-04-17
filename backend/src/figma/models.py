
from django.db import models
from django.contrib.auth.models import User
from utils.baseModel import BaseModel  # Corrected the import and naming convention


class Service(BaseModel):
    """
    Model for listing all services with new endpoints.
    

        
    Note:
        Register the names of the APIs you are using, such as OpenAIClient and openrouter.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, help_text='The user associated with the service.')
    service_name = models.CharField(max_length=200, unique=True, help_text='The name of the service.')
    is_service_active = models.BooleanField(default=True, help_text='Indicates if the service is active or not.')

    def __str__(self):
        return self.service_name


class UserApiInteractionHistory(BaseModel):
    """
    Model to keep the history of user interactions with the API Service.

        
    Note:

        This is a demo model. For further improvements, consider adding an api_response
        field to check if the API response was successful or failed.

    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, help_text='The user associated with the interaction.')
    user_prompt = models.TextField(help_text='The prompt or input from the user.')
    api_output = models.TextField(help_text='The output or response from the API.')
    api_service = models.ForeignKey(Service, on_delete=models.CASCADE, help_text='The associated service from the Service model.')

    def __str__(self):
        return f"User: {self.user.username}, Service: {self.api_service.service_name}"
