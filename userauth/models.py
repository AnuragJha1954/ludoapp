from django.db import models

# Create your models here.
from django.conf import settings

class OTPDetails(models.Model):
    phone_number = models.CharField(max_length=15)
    otp = models.CharField(max_length=6)

    def __str__(self):
        return f"OTP for phone number {self.phone_number}"