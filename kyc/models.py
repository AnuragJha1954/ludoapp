from django.db import models
from django.conf import settings

# Create your models here.

class KYCDetails(models.Model):
    STATUS_CHOICES = [
        ('P', 'Pending'),
        ('A', 'Approved'),
        ('D', 'Declined'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    document_number = models.CharField(max_length=100)
    front_side = models.ImageField(upload_to='kyc_documents/front/')
    back_side = models.ImageField(upload_to='kyc_documents/back/')
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')

    def __str__(self):
        return f"KYC details for {self.user.username} - {self.get_status_display()}"