from django.db import models


class BaseModel(models.Model):
    """
        
        This model defines base models that implements common fields like:
        
        created_at
        
        updated_at
        
          
    
    
    """
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        abstract = True  #