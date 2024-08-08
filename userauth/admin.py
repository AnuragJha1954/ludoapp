from django.contrib import admin

# Register your models here.
from .models import OTPDetails

@admin.register(OTPDetails)
class OTPDetailsAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'otp')
    search_fields = ('phone_number',)
    list_filter = ('phone_number',)
    ordering = ('phone_number',)
    readonly_fields = ('phone_number', 'otp')