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









class AdminDetails(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    commission_percentage = models.DecimalField(max_digits=5, decimal_places=2)  # To store commission in percentage
    upi_name = models.CharField(max_length=255)
    upi_id = models.CharField(max_length=255)
    upi_qr = models.ImageField(upload_to='admin_upi_qr/')  # Store the UPI QR code image
    whatsapp_number = models.CharField(max_length=15, blank=True, null=True)  # Add whatsapp_number field

    def __str__(self):
        return f"Admin Details for {self.user.username}"