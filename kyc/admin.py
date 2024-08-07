from django.contrib import admin
from .models import KYCDetails

class KYCDetailsAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'document_number', 'status')
    list_filter = ('status',)
    search_fields = ('user__username', 'full_name', 'document_number')


    fieldsets = (
        (None, {
            'fields': ('user', 'full_name', 'document_number', 'front_side', 'back_side', 'status')
        }),
    )

admin.site.register(KYCDetails, KYCDetailsAdmin)
