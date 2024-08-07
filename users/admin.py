from django.contrib import admin
from .models import CustomUser,AdminDetails
from django.contrib.auth.admin import UserAdmin

class CustomUserAdmin(UserAdmin):
    # fields to be displayed in the User admin form
    list_display = ['username', 'email', 'phone_number', 'verified']

    # fieldsets definition, including 'phone_number' and 'verified'
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'phone_number')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions', 'verified')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    # add_fieldsets definition if you're creating a new user from the admin panel
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'phone_number', 'password1', 'password2', 'verified'),
        }),
    )

# Register your models here.
admin.site.register(CustomUser, CustomUserAdmin)





@admin.register(AdminDetails)
class AdminDetailsAdmin(admin.ModelAdmin):
    list_display = ('user', 'commission_percentage', 'upi_name', 'upi_id', 'upi_qr')
    search_fields = ('user__username', 'upi_id')
    list_filter = ('commission_percentage',)