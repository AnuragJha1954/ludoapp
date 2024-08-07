from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class CustomUser(AbstractUser):
    # Add any additional fields you want here
    # Example:
    # age = models.IntegerField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    verified = models.BooleanField(default=False)
    kyc = models.BooleanField(default=False)
    
    def __str__(self):
        return self.username
